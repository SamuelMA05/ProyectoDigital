#include "xgpio.h"
#include "xiicps.h"
#include "xparameters.h"
#include "xil_printf.h"
#include "sleep.h"
#include <stdlib.h>
#include <string.h>
#include "xgpio.h"
#include "xiicps.h"
#include "xparameters.h"
#include "xil_printf.h"
#include "sleep.h"
#define I2C_DEVICE_ID        XPAR_XIICPS_0_DEVICE_ID
#define QMC5883_ADDR         0x0D
#define LCD_ADDR             0x27

#define GPIO_VERILOG_ID      XPAR_AXI_GPIO_2_DEVICE_ID
#define VERILOG_CHANNEL      1
void mostrar_lectura_magnetometro(int *x, int *y, int *z);
char* addCharMalloc(char *buffer, int *size, u32 data);
int writeReg_sensor(u8 reg, u8 value);
int readBytes_sensor(u8 reg, u8 *buffer, int len);
void lcd_init();
void lcd_set_cursor(int row, int col);
void lcd_print(const char *s);
void lcd_char(char c);
void lcd_send_byte(u8 value, u8 mode);
void crear_usuario_y_contrasena(XGpio *teclado);
void lcd_send_nibble(u8 nib, u8 mode);
void lcd_cmd(u8 cmd);
void lcd_i2c_write(u8 data);
void lcd_set_brightness(int percent);
int QMC_read6(u8 *buf);
int QMC_writeReg(u8 reg, u8 value);
int QMC_init();
u32 leer_tecla(XGpio *GpioVerilog);
int cambiar_contrasena(XGpio *teclado);
void lcd_clear();
int writeI2C(u8 addr, u8 *data, int len);
int readI2C(u8 addr, u8 reg, u8 *buffer, int len);
void welcome();
int comprobar_usuario(XGpio *teclado);
int mostrar_menu(XGpio *teclado);
//void pantalla_bienvenida(XGpio *teclado);

int menu_con_login(XGpio *teclado);

