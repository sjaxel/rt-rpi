# rt-rpi/device/registers.py
from abc import ABC, abstractmethod
from typing import Final, Iterator, Tuple
from smbus2 import SMBus


class RegisterIO(ABC):
    """
    Abstract base class for register I/O operations.
    
    This class defines the interface for reading and writing to registers.
    """

    @abstractmethod
    def read_register(self, reg: 'DeviceRegister') -> int:
        """
        Read a value from the specified register.
        
        Args:
            reg (DeviceRegister): The register to read from.
        
        Returns:
            int: The value read from the register.
        """
        pass

    @abstractmethod
    def write_register(self, reg: 'DeviceRegister', value: int):
        """
        Write a value to the specified register.
        
        Args:
            reg (DeviceRegister): The register to write to.
            value (int): The value to write to the register.
        """
        pass

class DeviceRegister():
    FLAG_READ: Final[int] = 'r'
    FLAG_WRITE: Final[int] = 'w'
    FLAG_VOLATILE: Final[int] = 'v'

    def __init__(self, address: int, reset_value: int, permissions: str):
        self.address = address
        self._reset_value = reset_value
        self.permissions = permissions
        self.io_handler: RegisterIO | None = None
        self._cache = None
        self._cache_valid = False

    def __set_name__(self, owner, name: str):
        """
        Set the name of the register when it is defined in a class.
        
        Args:
            owner: The class that owns this register.
            name (str): The name of the register.
        """
        self._name = name
        self._owner = owner


    @property
    def value(self) -> int:
        """
        Get the value of the register.
        
        Returns:
            int: The current value of the register.
        
        Notes:
            If the register is non-volatile and has been read before,
            returns the cached value to avoid unnecessary I/O operations.
        """
        if self.io_handler is None:
            raise AttributeError(f"Register '{self._name}' has no I/O handler set")
            
        # Use cached value for non-volatile registers if available
        if self._cache_valid and self.FLAG_VOLATILE not in self.permissions:
            return self._cache
            
        # Read from device for volatile registers or first read of non-volatile
        value = self.io_handler.read_register(self)
        
        # Cache the value for non-volatile registers
        if self.FLAG_VOLATILE not in self.permissions:
            self._cache = value
            self._cache_valid = True
            
        return value
    
    @value.setter
    def value(self, value: int):
        """
        Set the value of the register.
        
        Args:
            value (int): The new value for the register.
        
        Raises:
            AttributeError: If the register is read-only.
        """
        if self.io_handler is None:
            raise AttributeError(f"Register '{self._name}' has no I/O handler set")
            
        self.io_handler.write_register(self, value)
        
        # Update cache for non-volatile registers
        if self.FLAG_VOLATILE not in self.permissions:
            self._cache = value
            self._cache_valid = True
    
    def invalidate_cache(self):
        """
        Invalidate the cache for this register.
        
        This forces the next read to fetch from the actual device.
        """
        self._cache_valid = False

class I2CRegisterIO(RegisterIO):
    """ A concrete implementation of RegisterIO for I2C communication.
    This class uses the SMBus to read and write to registers.

    Args:
        bus (SMBus): The SMBus instance to use for I2C communication.
    """

    def __init__(self, i2c: SMBus, i2c_address: int):
        self.i2c = i2c
        self.i2c_address = i2c_address

    def read_register(self, reg: DeviceRegister) -> int:
        if DeviceRegister.FLAG_READ not in reg.permissions:
            raise AttributeError(f"Register '{reg._name}' is not readable")
        res = self.i2c.read_byte_data(self.i2c_address, reg.address)
        return res

    def write_register(self, reg: DeviceRegister, value: int):
        if DeviceRegister.FLAG_WRITE not in reg.permissions:
            raise AttributeError(f"Register '{reg._name}' is not writable")
        self.i2c.write_byte_data(self.i2c_address, reg.address, value)

class DeviceRegisters():
    def __init__(self, io_handler: RegisterIO):
        for reg in self.__class__.__dict__.values():
            if isinstance(reg, DeviceRegister):
                reg.io_handler = io_handler

    def list_all_cached(self) -> Iterator[Tuple[str, int]]:
        """
        List all cached registers and their values.
        
        Returns:
            Iterator[Tuple[str, int]]: An iterator over tuples containing register names and their cached values.
        """
        for reg in self.__class__.__dict__.values():
            if isinstance(reg, DeviceRegister) and reg._cache_valid:
                yield (reg._name, reg.value)