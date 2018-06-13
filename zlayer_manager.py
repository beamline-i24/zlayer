import pv, sys
import zlayer as zl
from ca import caget, caput

def initiate():
    energy = caget(pv.dcm_energy)
    det_dist = caget(pv.det_z)
    print 'Initiate GenPV'
    caput(pv.ioc12_gp1,  '/dls/i24/data/2017/cm16788-1')
    caput(pv.ioc12_gp2,  'zlayer-test')
    caput(pv.ioc12_gp3,  'zgrid')
    caput(pv.ioc12_gp5,  '0.01')
    caput(pv.ioc12_gp9,  10)
    caput(pv.ioc12_gp10, 10)
    caput(pv.ioc12_gp11, 10)
    caput(pv.ioc12_gp12, 10)
    caput(pv.ioc12_gp7,  str(det_dist))
    caput(pv.ioc12_gp13, 'control.inp')
    caput(pv.ioc12_gp15, 'initiate complete')
    return 1

def add_write():
    print 'Reading PVs',
    directory   = caget(pv.ioc12_gp1)
    subdir      = caget(pv.ioc12_gp2)
    filename    = caget(pv.ioc12_gp3)
    exp_time    = caget(pv.ioc12_gp5)
    step_size_x = caget(pv.ioc12_gp9)
    step_size_y = caget(pv.ioc12_gp10)
    num_of_x    = caget(pv.ioc12_gp11)
    num_of_y    = caget(pv.ioc12_gp12)
    energy      = 1000 * caget(pv.dcm_energy + '.RBV')
    det_dist    = caget(pv.ioc12_gp7)
    control_fid = caget(pv.ioc12_gp13)
    print 'Writing',
    g = open(control_fid, 'w')
    line1   = 'directory    (txt): %s\n' % directory 
    line2   = 'subdir      (txt): %s\n' % subdir 
    line3   = 'filename     (fid): %s\n' % filename
    line4   = 'exp_time     (sec): %s\n' % exp_time
    line5   = 'step_size_x   (mm): %s\n' % step_size_x 
    line6   = 'step_size_y   (mm): %s\n' % step_size_y
    line7   = 'num_of_x     (num): %s\n' % num_of_x 
    line8   = 'num_of_y     (num): %s\n' % num_of_y 
    line9   = 'energy        (eV): %s\n' % energy
    line10  = 'det_dist      (mm): %s\n' % det_dist
    line11  = 'control_fid (.inp): %s\n' % control_fid
    g.write(line1)
    g.write(line2)
    g.write(line3)
    g.write(line4)
    g.write(line5)
    g.write(line6)
    g.write(line7)
    g.write(line8)
    g.write(line9)
    g.write(line10)
    g.write(line11)
    g.close()
    return control_fid 

def main(arg):
    if 'initiate' in arg:
        initiate()
    elif 'run' in arg:
        control_fid = add_write()
        print 'Running zlayer_manager.py - run'
        zl.run(control_fid)
    else:
        print 'Unknown arg'
    print 10*'Done '
    
if __name__ == '__main__':
    main(sys.argv[1])
