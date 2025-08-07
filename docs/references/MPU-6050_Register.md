# MPU-6050 Register Definitions

The following table summarizes the register definitions for the MPU-6050 as referenced in section 3 "Register Map" of the datasheet.

| Register Name         | Address (Hex) | Description                                 |
|----------------------|---------------|---------------------------------------------|
| SELF_TEST_X          | 0x0D          | Self-Test Register for X-axis               |
| SELF_TEST_Y          | 0x0E          | Self-Test Register for Y-axis               |
| SELF_TEST_Z          | 0x0F          | Self-Test Register for Z-axis               |
| SELF_TEST_A          | 0x10          | Self-Test Register for Accelerometer        |
| SMPLRT_DIV           | 0x19          | Sample Rate Divider                        |
| CONFIG               | 0x1A          | Configuration                              |
| GYRO_CONFIG          | 0x1B          | Gyroscope Configuration                    |
| ACCEL_CONFIG         | 0x1C          | Accelerometer Configuration                |
| FIFO_EN              | 0x23          | FIFO Enable                                |
| I2C_MST_CTRL         | 0x24          | I2C Master Control                         |
| I2C_SLV0_ADDR        | 0x25          | I2C Slave 0 Address                        |
| I2C_SLV0_REG         | 0x26          | I2C Slave 0 Register                       |
| I2C_SLV0_CTRL        | 0x27          | I2C Slave 0 Control                        |
| I2C_SLV1_ADDR        | 0x28          | I2C Slave 1 Address                        |
| I2C_SLV1_REG         | 0x29          | I2C Slave 1 Register                       |
| I2C_SLV1_CTRL        | 0x2A          | I2C Slave 1 Control                        |
| I2C_SLV2_ADDR        | 0x2B          | I2C Slave 2 Address                        |
| I2C_SLV2_REG         | 0x2C          | I2C Slave 2 Register                       |
| I2C_SLV2_CTRL        | 0x2D          | I2C Slave 2 Control                        |
| I2C_SLV3_ADDR        | 0x2E          | I2C Slave 3 Address                        |
| I2C_SLV3_REG         | 0x2F          | I2C Slave 3 Register                       |
| I2C_SLV3_CTRL        | 0x30          | I2C Slave 3 Control                        |
| I2C_SLV4_ADDR        | 0x31          | I2C Slave 4 Address                        |
| I2C_SLV4_REG         | 0x32          | I2C Slave 4 Register                       |
| I2C_SLV4_DO          | 0x33          | I2C Slave 4 Data Out                       |
| I2C_SLV4_CTRL        | 0x34          | I2C Slave 4 Control                        |
| I2C_SLV4_DI          | 0x35          | I2C Slave 4 Data In                        |
| I2C_MST_STATUS       | 0x36          | I2C Master Status                          |
| INT_PIN_CFG          | 0x37          | Interrupt Pin/Bypass Enable Configuration  |
| INT_ENABLE           | 0x38          | Interrupt Enable                           |
| INT_STATUS           | 0x3A          | Interrupt Status                           |
| ACCEL_XOUT_H         | 0x3B          | Accelerometer X-axis High Byte             |
| ACCEL_XOUT_L         | 0x3C          | Accelerometer X-axis Low Byte              |
| ACCEL_YOUT_H         | 0x3D          | Accelerometer Y-axis High Byte             |
| ACCEL_YOUT_L         | 0x3E          | Accelerometer Y-axis Low Byte              |
| ACCEL_ZOUT_H         | 0x3F          | Accelerometer Z-axis High Byte             |
| ACCEL_ZOUT_L         | 0x40          | Accelerometer Z-axis Low Byte              |
| TEMP_OUT_H           | 0x41          | Temperature High Byte                      |
| TEMP_OUT_L           | 0x42          | Temperature Low Byte                       |
| GYRO_XOUT_H          | 0x43          | Gyroscope X-axis High Byte                 |
| GYRO_XOUT_L          | 0x44          | Gyroscope X-axis Low Byte                  |
| GYRO_YOUT_H          | 0x45          | Gyroscope Y-axis High Byte                 |
| GYRO_YOUT_L          | 0x46          | Gyroscope Y-axis Low Byte                  |
| GYRO_ZOUT_H          | 0x47          | Gyroscope Z-axis High Byte                 |
| GYRO_ZOUT_L          | 0x48          | Gyroscope Z-axis Low Byte                  |
| USER_CTRL            | 0x6A          | User Control                               |
| PWR_MGMT_1           | 0x6B          | Power Management 1                         |
| PWR_MGMT_2           | 0x6C          | Power Management 2                         |
| FIFO_COUNTH          | 0x72          | FIFO Count High Byte                       |
| FIFO_COUNTL          | 0x73          | FIFO Count Low Byte                        |
| FIFO_R_W             | 0x74          | FIFO Read/Write                            |
| WHO_AM_I             | 0x75          | Device ID                                  |

*Note: This table lists commonly used registers. Refer to the official datasheet for the complete register map and detailed