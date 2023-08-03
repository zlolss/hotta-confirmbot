import subprocess
import sys

class Device:
    def __init__(self, device_id = None):
        self.id = device_id
        
    @property    
    def adbhead(self):
        if self.id:
            return f'adb -s {self.id} '
        return 'adb '
        
    def adb(self, cmd, readout=True):
        acmd = self.adbhead+cmd
        subp =  subprocess.Popen(acmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        if readout:
            return subp.stdout.read().decode()
        return subp
        
    def shell(self, cmd, readout=True):
        return self.adb(f'shell "{cmd}"', readout)
        
    def getOrientation(self):
        #0 原始竖屏， 1 左横屏， 3 右横屏
        return int(self.shell("dumpsys input| grep \'SurfaceOrientation:\' | head -1", readout=True).split()[-1])
        
    @property    
    def ABI(self):
        pname =f'_{sys._getframe().f_code.co_name}'
        if pname not in vars(self):
            vars(self)[pname] = self.shell("getprop ro.product.cpu.abi", readout=True).strip()
        return vars(self)[pname]
    
    @property
    def abi(self):
        return self.ABI
            
    @property    
    def SDK(self):
        pname =f'_{sys._getframe().f_code.co_name}'
        if pname not in vars(self):
            self.__dict__[pname] = int(self.shell("getprop ro.build.version.sdk", readout=True).strip())
        return vars(self)[pname]      

    @property
    def sdk(self):
        return self.SDK
        
    
    
    
    