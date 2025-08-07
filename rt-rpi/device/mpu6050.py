from enum import IntEnum, Flag, IntFlag, nonmember
import enum
import time
import struct
from smbus2 import SMBus, i2c_msg


from core.log import logging, init_log_config
from .registers import DeviceRegister, DeviceRegisters, I2CRegisterIO


class MPU6050Registers(DeviceRegisters):
    """ A class representing the registers of the MPU6050 device.
    This class defines the registers and their properties.
    """

    # Self-Test Registers
    SELF_TEST_X = DeviceRegister(0x0D, 0, "rv")
    SELF_TEST_Y = DeviceRegister(0x0E, 0, "rv")
    SELF_TEST_Z = DeviceRegister(0x0F, 0, "rv")
    SELF_TEST_A = DeviceRegister(0x10, 0, "rv")
    
    # Configuration Registers
    SMPLRT_DIV = DeviceRegister(0x19, 0, "rw")
    CONFIG = DeviceRegister(0x1A, 0, "rw")
    GYRO_CONFIG = DeviceRegister(0x1B, 0, "rw")
    ACCEL_CONFIG = DeviceRegister(0x1C, 0, "rw")
    
    # FIFO Enable
    FIFO_EN = DeviceRegister(0x23, 0, "rwv")
    
    # I2C Master Control
    I2C_MST_CTRL = DeviceRegister(0x24, 0, "rwv")
    I2C_SLV0_ADDR = DeviceRegister(0x25, 0, "rwv")
    I2C_SLV0_REG = DeviceRegister(0x26, 0, "rwv")
    I2C_SLV0_CTRL = DeviceRegister(0x27, 0, "rwv")
    I2C_SLV1_ADDR = DeviceRegister(0x28, 0, "rwv")
    I2C_SLV1_REG = DeviceRegister(0x29, 0, "rwv")
    I2C_SLV1_CTRL = DeviceRegister(0x2A, 0, "rwv")
    I2C_SLV2_ADDR = DeviceRegister(0x2B, 0, "rwv")
    I2C_SLV2_REG = DeviceRegister(0x2C, 0, "rwv")
    I2C_SLV2_CTRL = DeviceRegister(0x2D, 0, "rwv")
    I2C_SLV3_ADDR = DeviceRegister(0x2E, 0, "rwv")
    I2C_SLV3_REG = DeviceRegister(0x2F, 0, "rwv")
    I2C_SLV3_CTRL = DeviceRegister(0x30, 0, "rwv")
    I2C_SLV4_ADDR = DeviceRegister(0x31, 0, "rwv")
    I2C_SLV4_REG = DeviceRegister(0x32, 0, "rwv")
    I2C_SLV4_DO = DeviceRegister(0x33, 0, "rwv")
    I2C_SLV4_CTRL = DeviceRegister(0x34, 0, "rwv")
    I2C_SLV4_DI = DeviceRegister(0x35, 0, "rv")
    I2C_MST_STATUS = DeviceRegister(0x36, 0, "rv")
    
    # Interrupt Configuration
    INT_PIN_CFG = DeviceRegister(0x37, 0, "rwv")
    INT_ENABLE = DeviceRegister(0x38, 0, "rwv")
    INT_STATUS = DeviceRegister(0x3A, 0, "rv")
    
    # Accelerometer Measurements
    ACCEL_XOUT_H = DeviceRegister(0x3B, 0, "rv")
    ACCEL_XOUT_L = DeviceRegister(0x3C, 0, "rv")
    ACCEL_YOUT_H = DeviceRegister(0x3D, 0, "rv")
    ACCEL_YOUT_L = DeviceRegister(0x3E, 0, "rv")
    ACCEL_ZOUT_H = DeviceRegister(0x3F, 0, "rv")
    ACCEL_ZOUT_L = DeviceRegister(0x40, 0, "rv")
    
    # Temperature Measurement
    TEMP_OUT_H = DeviceRegister(0x41, 0, "rv")
    TEMP_OUT_L = DeviceRegister(0x42, 0, "rv")
    
    # Gyroscope Measurements
    GYRO_XOUT_H = DeviceRegister(0x43, 0, "rv")
    GYRO_XOUT_L = DeviceRegister(0x44, 0, "rv")
    GYRO_YOUT_H = DeviceRegister(0x45, 0, "rv")
    GYRO_YOUT_L = DeviceRegister(0x46, 0, "rv")
    GYRO_ZOUT_H = DeviceRegister(0x47, 0, "rv")
    GYRO_ZOUT_L = DeviceRegister(0x48, 0, "rv")
    
    # External Sensor Data
    EXT_SENS_DATA_00 = DeviceRegister(0x49, 0, "rv")
    EXT_SENS_DATA_01 = DeviceRegister(0x4A, 0, "rv")
    EXT_SENS_DATA_02 = DeviceRegister(0x4B, 0, "rv")
    EXT_SENS_DATA_03 = DeviceRegister(0x4C, 0, "rv")
    EXT_SENS_DATA_04 = DeviceRegister(0x4D, 0, "rv")
    EXT_SENS_DATA_05 = DeviceRegister(0x4E, 0, "rv")
    EXT_SENS_DATA_06 = DeviceRegister(0x4F, 0, "rv")
    EXT_SENS_DATA_07 = DeviceRegister(0x50, 0, "rv")
    EXT_SENS_DATA_08 = DeviceRegister(0x51, 0, "rv")
    EXT_SENS_DATA_09 = DeviceRegister(0x52, 0, "rv")
    EXT_SENS_DATA_10 = DeviceRegister(0x53, 0, "rv")
    EXT_SENS_DATA_11 = DeviceRegister(0x54, 0, "rv")
    EXT_SENS_DATA_12 = DeviceRegister(0x55, 0, "rv")
    EXT_SENS_DATA_13 = DeviceRegister(0x56, 0, "rv")
    EXT_SENS_DATA_14 = DeviceRegister(0x57, 0, "rv")
    EXT_SENS_DATA_15 = DeviceRegister(0x58, 0, "rv")
    EXT_SENS_DATA_16 = DeviceRegister(0x59, 0, "rv")
    EXT_SENS_DATA_17 = DeviceRegister(0x5A, 0, "rv")
    EXT_SENS_DATA_18 = DeviceRegister(0x5B, 0, "rv")
    EXT_SENS_DATA_19 = DeviceRegister(0x5C, 0, "rv")
    EXT_SENS_DATA_20 = DeviceRegister(0x5D, 0, "rv")
    EXT_SENS_DATA_21 = DeviceRegister(0x5E, 0, "rv")
    EXT_SENS_DATA_22 = DeviceRegister(0x5F, 0, "rv")
    EXT_SENS_DATA_23 = DeviceRegister(0x60, 0, "rv")
    
    # I2C Slave Data Out
    I2C_SLV0_DO = DeviceRegister(0x63, 0, "rwv")
    I2C_SLV1_DO = DeviceRegister(0x64, 0, "rwv")
    I2C_SLV2_DO = DeviceRegister(0x65, 0, "rwv")
    I2C_SLV3_DO = DeviceRegister(0x66, 0, "rwv")
    
    # I2C Master Delay Control
    I2C_MST_DELAY_CTRL = DeviceRegister(0x67, 0, "rwv")
    
    # Signal Path Reset
    SIGNAL_PATH_RESET = DeviceRegister(0x68, 0, "rwv")
    
    # Motion Detection Control
    MOT_DETECT_CTRL = DeviceRegister(0x69, 0, "rwv")
    
    # User Control
    USER_CTRL = DeviceRegister(0x6A, 0, "rwv")
    
    # Power Management
    PWR_MGMT_1 = DeviceRegister(0x6B, 0x40, "rw")
    PWR_MGMT_2 = DeviceRegister(0x6C, 0, "rw")
    
    # FIFO Count Registers
    FIFO_COUNTH = DeviceRegister(0x72, 0, "rv")
    FIFO_COUNTL = DeviceRegister(0x73, 0, "rv")
    
    # FIFO Read/Write
    FIFO_R_W = DeviceRegister(0x74, 0, "rwv")
    
    # Who Am I
    WHO_AM_I = DeviceRegister(0x75, 0x68, "rv")

    def __init__(self, i2c: SMBus, i2c_address: int):
        self.io_handler = I2CRegisterIO(i2c, i2c_address)
        super().__init__(self.io_handler)



class GyroConfig(IntFlag):
    """Gyroscope configuration options"""
    REGISTER_BASE = 0x37
    RANGE_250_DEG = 0x00 << 3  # ± 250 °/s
    RANGE_500_DEG = 0x01 << 3  # ± 500 °/s
    RANGE_1000_DEG = 0x02 << 3  # ± 1000 °/s
    RANGE_2000_DEG = 0x03 << 3  # ± 2000 °/s


class AccelConfig(IntFlag):
    """Accelerometer configuration options"""
    RANGE_2_G = 0x00 << 3  # ± 2g
    RANGE_4_G = 0x01 << 3  # ± 4g
    RANGE_8_G = 0x02 << 3  # ± 8g
    RANGE_16_G = 0x03 << 3  # ± 16g


class PowerManagement1(IntFlag):
    """Power management 1 register bits"""
    DEVICE_RESET = 0x80
    SLEEP = 0x40
    CYCLE = 0x20
    TEMP_DIS = 0x08
    CLKSEL_INTERNAL = 0x00
    CLKSEL_PLL_X_GYRO = 0x01
    CLKSEL_PLL_Y_GYRO = 0x02
    CLKSEL_PLL_Z_GYRO = 0x03
    CLKSEL_PLL_EXT_32K = 0x04
    CLKSEL_PLL_EXT_19M = 0x05
    CLKSEL_STOP = 0x07


class InterruptEnable(IntFlag):
    """Interrupt enable register bits"""

    DATA_RDY_EN = 0x01
    I2C_MST_INT_EN = 0x08
    FIFO_OFLOW_EN = 0x10
    MOT_EN = 0x40

class DLPF_CFG(IntFlag):
    """Digital Low Pass Filter configuration options"""
    DLPF_CFG_BW256HZ_NOLPF = 0x00  # 256 Hz, no LPF
    DLPF_CFG_BW188HZ = 0x01         # 188 Hz
    DLPF_CFG_BW98HZ = 0x02          # 98 Hz
    DLPF_CFG_BW42HZ = 0x03          # 42 Hz
    DLPF_CFG_BW20HZ = 0x04          # 20 Hz
    DLPF_CFG_BW10HZ = 0x05          # 10 Hz
    DLPF_CFG_BW5HZ = 0x06           # 5 Hz
    DLPF_CFG_RESERVED = 0x07         # No LPF

class ACCEL_LSB_SCALE(IntEnum):
    """Accelerometer LSB scale factors for different ranges"""
    RANGE_2_G = 16384  # ± 2g
    RANGE_4_G = 8192   # ± 4g
    RANGE_8_G = 4096   # ± 8g
    RANGE_16_G = 2048  # ± 16g

class GYRO_LSB_SCALE(IntEnum):
    """Gyroscope LSB scale factors for different ranges"""
    RANGE_250_DEG = 131  # ± 250 °/s
    RANGE_500_DEG = 65.5  # ± 500 °/s
    RANGE_1000_DEG = 32.8  # ± 1000 °/s
    RANGE_2000_DEG = 16.4  # ± 2000 °/s


class MPU6050:
    """Driver for the MPU-6050 6-axis IMU"""
    
    # Default I2C address
    DEFAULT_ADDRESS = 0x68
    
    def __init__(self, i2c_bus: int | str, address=DEFAULT_ADDRESS):
        """
        Initialize the MPU-6050 driver.
        
        Args:
            i2c_bus: I2C bus number or path (e.g., 1 or '/dev/i2c-1')
            address: I2C address of the MPU-6050 (default: 0x68)
        """
        self.i2c: SMBus = SMBus()
        self._i2c_bus: int | str = i2c_bus
        self.address = address
        self._logger = logging.getLogger("MPU6050")
        self.reg = MPU6050Registers(self.i2c, self.address)


    def _device_init(self):
        """
        Initialize the MPU-6050 device.
        This method should be called after opening the I2C bus.
        """
        # Reset the device
        self.reset()
        # Set clock source to PLL with X Gyro
        self.reg.PWR_MGMT_1.value = PowerManagement1.CLKSEL_PLL_X_GYRO
        # Set accelerometer and gyroscope configurations

    def connected(self) -> bool:
        """
        Check if the MPU-6050 is connected by reading the WHO_AM_I register.
        
        Returns:
            bool: True if the device is connected, False otherwise.
        """
        try:
            return self.reg.WHO_AM_I.value == self.address            
        except Exception as e:
            print(f"Error checking connection: {e}")
            return False

    def reset(self):
        """
        Reset the MPU-6050 device.
        This will reset the device and reinitialize it.
        """
        self.reg.PWR_MGMT_1.value = PowerManagement1.DEVICE_RESET
        time.sleep(0.1)  # Wait for the reset to complete
        if not self.connected():
            raise RuntimeError("Failed to reset MPU-6050, device not connected")

    def read_raw_measurments(self) -> bytes:
        """
        Read measurements from the MPU-6050 device.

        This uses a bulk read to get all sensor data in one go.
        """

        data = self.i2c.read_i2c_block_data(self.address, self.reg.ACCEL_XOUT_H.address, 14)
        return bytes(data)

    def read_measurments(self) -> dict[str, dict[str, float] | float]:
        """
        Read measurements from the MPU-6050 device and unpack them into a dictionary.

        Returns:
            dict: A dictionary containing the accelerometer (x, y, z), temperature, and gyroscope (x, y, z) values.
        """
        data = self.read_raw_measurments()
        accel_x, accel_y, accel_z, temp, gyro_x, gyro_y, gyro_z = struct.unpack('>hhhhhhh', data)
        
        # Convert raw values to physical units
        accel_x /= ACCEL_LSB_SCALE.RANGE_2_G
        accel_y /= ACCEL_LSB_SCALE.RANGE_2_G
        accel_z /= ACCEL_LSB_SCALE.RANGE_2_G
        gyro_x /= GYRO_LSB_SCALE.RANGE_250_DEG
        gyro_y /= GYRO_LSB_SCALE.RANGE_250_DEG
        gyro_z /= GYRO_LSB_SCALE.RANGE_250_DEG
        temp = (temp / 340.0) + 36.53  # Convert to Celsius

        return {
            'gyro': {
                'x': gyro_x,
                'y': gyro_y,
                'z': gyro_z
            },
            'accel': {
                'x': accel_x,
                'y': accel_y,
                'z': accel_z
            },
            'temp': temp,
        }

    @property
    def gyro_config(self) -> GyroConfig:
        """
        Get the gyroscope configuration.

        Returns:
            GyroConfig: The current value of the gyroscope configuration.
        """
        return GyroConfig(self.reg.GYRO_CONFIG.value)

    @gyro_config.setter
    def gyro_config(self, value: GyroConfig):
        """
        Set the gyroscope configuration.
        
        Args:
            value: GyroConfig enum value to set the gyroscope range.
        """
        if isinstance(value, GyroConfig):
            self.reg.GYRO_CONFIG.value = value
            self._logger.info(f"[SET] Gyro Config: {value.name}")
        else:
            raise ValueError("Invalid GyroConfig value")
        
    @property
    def accel_config(self) -> AccelConfig:
        """
        Get the accelerometer configuration.
        
        Returns:
            AccelConfig: The current value of the accelerometer configuration.
        """
        return AccelConfig(self.reg.ACCEL_CONFIG.value)

    @accel_config.setter
    def accel_config(self, value: AccelConfig):
        """
        Set the accelerometer configuration.
        
        Args:
            value: AccelConfig enum value to set the accelerometer range.
        """
        if isinstance(value, AccelConfig):
            self.reg.ACCEL_CONFIG.value = value
            self._logger.info(f"[SET] Accel Config: {value.name}")
        else:
            raise ValueError("Invalid AccelConfig value")
        
    @property
    def int_enable(self) -> InterruptEnable:
        """ Get the interrupt enable register value.
        Returns:
            InterruptEnable: The current value of the interrupt enable register.

        """
        return InterruptEnable(self.reg.INT_ENABLE.value)

    @int_enable.setter
    def int_enable(self, value: InterruptEnable):
        """
        Set the interrupt enable register value.
        
        Args:
            value: The value to set for the interrupt enable register.
        """
        if not isinstance(value, InterruptEnable):
            raise ValueError("Interrupt enable value must be an instance of InterruptEnable")
        self.reg.INT_ENABLE.value = value
        self._logger.info(f"[SET] Interrupt Enable: {value.name}")

    def raw_gyro_odr(self) -> int:
        """
        Get the raw gyroscope output data rate (ODR).
        
        Returns:
            float: The raw ODR in Hz.
        """
        dlpf_cfg = self.reg.CONFIG.value & 0x07  # Get DLPF_CFG bits
        if dlpf_cfg == DLPF_CFG.DLPF_CFG_BW256HZ_NOLPF:
            return int(8 * 1e3)  # 8 kHz
        else:
            return int(1e3)

    @property
    def sample_rate(self) -> int:
        """
        The output data  rate (ODR) of the device.

        The ODR is calculated based on the DLPF configuration and the SMPLRT_DIV register.

        Accelerometer is sampled at max 1 khz so for higher ODRs, the same sample
        might be output multiple times from the accelerometer FIFO.
        
        Returns:
            int: The output data rate in Hz.
        """
        # The raw gyro data rate is dependent on DLPF and SMPLRT_DIV
        raw_gyro_odr = self.raw_gyro_odr()
        # Get the SMPLRT_DIV value
        smplrt_div = self.reg.SMPLRT_DIV.value
        # Calculate the effective ODR
        return int(raw_gyro_odr / (smplrt_div + 1))

    @sample_rate.setter
    def sample_rate(self, value: int):
        """
        Set the output data rate (ODR) of the device.
        
        Args:
            value: Desired ODR in Hz.
        """
        if value <= 0:
            raise ValueError("Sample rate must be a positive integer")
        
        # Calculate SMPLRT_DIV based on the desired sample rate
        raw_gyro_odr = self.raw_gyro_odr()
        smplrt_div = int(raw_gyro_odr / value) - 1

        if smplrt_div > 0xFF:
            raise ValueError(f"Sample rate {value} Hz is too low, maximum is {raw_gyro_odr // 256} Hz")


        self.reg.SMPLRT_DIV.value = smplrt_div
        self._logger.info(f"[SET] Sample Rate: {value} Hz (SMPLRT_DIV: {smplrt_div})")

    def int_status(self, mask: InterruptEnable = InterruptEnable.DATA_RDY_EN) -> InterruptEnable:
        """
        Get the interrupt status for the specified mask.

        Args:
            mask: The interrupt mask to check.

        Returns:
            bool: True if the interrupt is active, False otherwise.
        """
        return InterruptEnable(self.reg.INT_STATUS.value & mask.value)

    def __enter__(self):
        """
        Context manager entry method to open the I2C bus.
        """
        self.open()
        self._device_init()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit method to close the I2C bus.
        """
        self.close()

    def open(self):
        """
        Open the I2C bus.
        """
        self.i2c.open(self._i2c_bus)

    def close(self):
        """
        Close the I2C bus.
        """
        self.i2c.close()
    


if __name__ == "__main__":
    # Example usage
    init_log_config()
    logger = logging.getLogger("MPU6050Example")


    with MPU6050(1) as mpu:  # Use the appropriate bus number
        if not mpu.connected():
            logger.error("MPU-6050 not connected")
            raise ConnectionError("MPU-6050 not connected")
        else:
            logger.info("MPU-6050 connected successfully")

        # Set gyroscope and accelerometer configurations
        mpu.gyro_config = GyroConfig.RANGE_250_DEG
        mpu.accel_config = AccelConfig.RANGE_2_G

        # Set sample rate
        mpu.sample_rate = 40
        # Set the DR interrupt enable
        mpu.int_enable = InterruptEnable.DATA_RDY_EN

        # Poll interrupt status and track time between data samples.
        start_time = time.time()
        n_samples = 0
        while True:
            try:
                if mpu.int_status(InterruptEnable.DATA_RDY_EN):
                    n_samples += 1
                    data = mpu.read_measurments()
                    logger.info(f" Sample {n_samples}: "
                                f"Accel: ({data['accel']['x']:.2f}, {data['accel']['y']:.2f}, {data['accel']['z']:.2f}), "
                                f"Gyro: ({data['gyro']['x']:.2f}, {data['gyro']['y']:.2f}, {data['gyro']['z']:.2f}), "
                                f"Temp: {data['temp']:.2f} °C")
            except KeyboardInterrupt:
                logger.info("Exiting data polling loop")
                break
            except Exception as e:
                logger.error(f"Error during data polling: {e}")
                raise e
                break
        elapsed = time.time() - start_time
        avarage_elapsed = elapsed / n_samples if n_samples > 0 else 0
        logger.info(f"Average sample frequency: {1.0 / avarage_elapsed:.2f} Hz")

