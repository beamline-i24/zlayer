#!/usr/bin/python
import pv
from time import sleep
from ca import caput, caget 
import setup_beamline as sup
import os, re, sys, math, time

#####     This supercedes Gold Digger and Gold Rush    #####
def print_flush(text):
    sys.stdout.write(str(text))
    sys.stdout.flush()

def scrape_control(control_fid):
    f = open(control_fid)
    for line in f.readlines():
        print '\t', line.rstrip()
        entry = line.rstrip('\n').split(':')
        k, v = entry[0], entry[1].strip().strip('/')
        if k.startswith('dir'):
            directory = str(v)
        elif k.startswith('subdir'):
            subdir = str(v)
        elif k.startswith('filename'):
            filename = str(v)
        elif k.startswith('exp_time'):
            exp_time = float(v)
        elif k.startswith('step_size_x'):
            step_size_x = float(v)
        elif k.startswith('step_size_y'):
            step_size_y = float(v)
        elif k.startswith('num_of_x'):
            num_of_x = int(v)
        elif k.startswith('num_of_y'):
            num_of_y = int(v)
        elif k.startswith('energy'):
            energy =  float(v)
        elif k.startswith('det_dist'):
            det_dist =  float(v)
        else:
 	    print 'Error in scrape_control', k
    f.close()
    return [directory, subdir, filename, exp_time, step_size_x, step_size_y, num_of_x, num_of_y, energy, det_dist]

def grid_cs_maker():
    print 'Make CS system'
    # get omega and alpha from GDA
    #For testing
    gridomega = ca.caget(pv.vgon_omega) #0
    gridomegaR = math.radians(gridomega)
    gridalpha = 0 # ca.caget(pv.vgon_kappa)
    gridalphaR = math.radians(gridalpha)
    # Motor counts to mm
    smarscale  = 1./ca.caget(pv.vgon_pinxs + '.MRES') #10000
    huberscale = 1./ca.caget(pv.vgon_pinyh + '.MRES') #50000
    #Evaluate numbers. Careful with scale
    x1factor =  -1*math.cos(gridomegaR) * smarscale
    y1factor =  0
    z1factor =  -1*math.sin(gridomegaR) * smarscale
    x2factor =  0
    y2factor =  1                    * huberscale
    z2factor =  0
    x3factor =  -math.sin(gridomegaR)* smarscale
    y3factor =  0
    z3factor =  math.cos(gridomegaR) * smarscale

    cs1 = "&4#3->%+1.2fX%+1.2fY%+1.2fZ" % (x1factor, y1factor, z1factor) #xstage
    cs2 = "&4#9->%+1.2fX%+1.2fY%+1.2fZ" % (x2factor, y2factor, z2factor) #ystage
    cs3 = "&4#1->%+1.2fX%+1.2fY%+1.2fZ" % (x3factor, y3factor, z3factor) #zstage
    print '\n'.join([cs1, cs2, cs3])   
    # Move CS to PMAC
    """
    caput(pv.step10_pmac_str, cs1)
    sleep(0.2)
    caput(pv.step10_pmac_str, cs2)
    sleep(0.2)

    print 'PIN Grid CS maker done'
    """
    print 2*'\n'

def load_motion_program_data(num_of_x, num_of_y, step_size_x, step_size_y, exp_time, xs_start, yh_start, zs_start):
    print '\n***** Entering load_motion_program_data'
    caput(pv.step10_pmac_str,'P2411 = %s'%num_of_x)  
    caput(pv.step10_pmac_str,'P2412 = %s'%num_of_y)   
    caput(pv.step10_pmac_str,'P2413 = %s'%str(float(step_size_x)/1000.))   
    caput(pv.step10_pmac_str,'P2414 = %s'%str(float(step_size_y)/1000.))
    caput(pv.step10_pmac_str,'P2415 = %s'%str(float(exp_time)*1000))
    caput(pv.step10_pmac_str,'P2416 = %s'%xs_start)   
    caput(pv.step10_pmac_str,'P2417 = %s'%yh_start)
    caput(pv.step10_pmac_str,'P2418 = %s'%zs_start)
    print '***** leaving load_motion_program_data'
    return 0 

def run(control_fid):
    if control_fid:
        print control_fid
    else:
        print 'Expected control.inp'
        return 0

    [directory, subdir, filename, exp_time, step_size_x, step_size_y, num_of_x, num_of_y, energy, det_dist] \
                                                                               =  scrape_control(control_fid)

    total_numb_imgs = num_of_x * num_of_y
    filepath = os.path.join(directory, subdir)
    print 'Total number of images: ', total_numb_imgs
    print 'File Path: ', filepath
    sup.beamline('zlayer', [det_dist])
    sup.pilatus('zlayer', [filepath, filename, total_numb_imgs, exp_time])
    sup.zebra1('zlayer', [])
    sup.xspress3('zlayer', [filepath, filename, total_numb_imgs])
    sup.geobrick('zlayer', [])

    print 'Move to XY Start'
    grid_cs_maker()
    xs_start = caget(pv.vgon_pinxs)
    yh_start = caget(pv.vgon_pinyh)
    zs_start = caget(pv.vgon_pinzs)
    omega_start = caget(pv.vgon_omega)
    load_motion_program_data(num_of_x, num_of_y, step_size_x, step_size_y, exp_time, xs_start, yh_start, zs_start)

    print 'pilatus acquire ON'
    caput(pv.pilat_acquire, '1')
    sleep(0.2)
    caput(pv.pilat_acquire, '1')
    caput(pv.xsp3_acquire, '1')
    caput(pv.zebra1_pc_arm, '1')

    print '\n\nCollection Area \n\n'
    print 20*'\nTHIS NEEDS TO BE FINALIZED. THIS IS NOT A WORKING VERSION'
    caput(pv.step10_pmac_str, '&4b24r')
    sleep(1)
 
    i=0 
    text_list = ['|', '/', '-', '\\']
    caput(pv.ioc12_gp8, 0)
    while caget(pv.pmc_gridstatus) == 1 or caget(pv.pmc_gridcounter) != total_numb_imgs:
	line_of_text = '\r\t\t\t Waiting   ' + 30*('%s' %text_list[i%4])
	print_flush(line_of_text)
	sleep(0.5)
        i += 1
	if caget(pv.ioc12_gp8) != 0:
	    print 50*'ABORTED '
	    caput(pv.pilat_acquire, 0)
	    break
        if caget(pv.zebra1_pc_arm_out) != 1:
            print ' ----> Zebra Disarmed <----- '
	    break

    print 'Return to Normal'
    sup.beamline('return-to-normal')
    sup.pilatus('return-to-normal')
    sup.zebra1('return-to-normal')
    sup.xspress3('return-to-normal')
    sup.geobrick('return-to-normal')

    print 'EOP'
    
if __name__ == '__main__':
    main(sys.argv[1])
