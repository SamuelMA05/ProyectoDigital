#include "Funciones.h"
#include <math.h>


XIicPs Iic;
char* addCharMalloc(char *buffer, int *size, u32 data)
{

    if (buffer == NULL) {
        buffer = (char*)malloc(2);  // 1 char + '\0'
        buffer[0] = (char)data;
        buffer[1] = '\0';
        *size = 1;
        return buffer;
    }


    char *temp = (char*)realloc(buffer, (*size + 2));
    if (temp == NULL) {
        return buffer;  // si falla, mantén el original
    }

    buffer = temp;
    buffer[*size] = (char)data;  // Agregar el caracter nuevo
    (*size)++;
    buffer[*size] = '\0';       // Mantener string válido

    return buffer;
}
int writeI2C(u8 addr, u8 *data, int len)
{
    int status = XIicPs_MasterSendPolled(&Iic, data, len, addr);
    while (XIicPs_BusIsBusy(&Iic));
    return status;
}

int readI2C(u8 addr, u8 reg, u8 *buffer, int len)
{
    int status;
    status = XIicPs_MasterSendPolled(&Iic, &reg, 1, addr);
    while (XIicPs_BusIsBusy(&Iic));
    if (status != XST_SUCCESS) return XST_FAILURE;
    status = XIicPs_MasterRecvPolled(&Iic, buffer, len, addr);
    while (XIicPs_BusIsBusy(&Iic));
    return status;
}

#define REG_X_LSB    0x00
#define REG_CTRL1    0x09
#define REG_CTRL2    0x0A
#define REG_RESET    0x0B

int QMC_writeReg(u8 reg, u8 value)
{
    u8 d[2] = {reg, value};
    return writeI2C(QMC5883_ADDR, d, 2);
}

int QMC_read6(u8 *buf)
{
    return readI2C(QMC5883_ADDR, REG_X_LSB, buf, 6);
}

int QMC_init()
{
    if (QMC_writeReg(REG_RESET, 0x01) != XST_SUCCESS)
        return XST_FAILURE;
    usleep(10000);
    if (QMC_writeReg(REG_CTRL1, 0b00011101) != XST_SUCCESS)
        return XST_FAILURE;
    if (QMC_writeReg(REG_CTRL2, 0x00) != XST_SUCCESS)
        return XST_FAILURE;
    return XST_SUCCESS;
}

u8 lcd_backlight = 0x08;

void lcd_clear()
{
    lcd_cmd(0x01);   // Limpia la pantalla
    usleep(2000);    // Tiempo necesario para completar el comando
}


void lcd_set_brightness(int percent)
{
    if (percent >= 100)
        lcd_backlight = 0x08;
    else if (percent <= 0)
        lcd_backlight = 0x00;
    else if (percent <= 50)
        lcd_backlight = 0x00;
    else
        lcd_backlight = 0x08;
}

void lcd_i2c_write(u8 data)
{
    writeI2C(LCD_ADDR, &data, 1);
}

void lcd_send_nibble(u8 nib, u8 mode)
{
    u8 data = nib | lcd_backlight | mode;
    lcd_i2c_write(data | 0x04);
    usleep(1);
    lcd_i2c_write(data & ~0x04);
    usleep(40);
}

void lcd_send_byte(u8 value, u8 mode)
{
    lcd_send_nibble(value & 0xF0, mode);
    lcd_send_nibble((value << 4) & 0xF0, mode);
}

void lcd_cmd(u8 cmd)
{
    lcd_send_byte(cmd, 0x00);
    usleep(2000);
}

void lcd_char(char c)
{
    lcd_send_byte(c, 0x01);
}

void lcd_print(const char *s)
{
    while (*s) lcd_char(*s++);
}

void lcd_set_cursor(int row, int col)
{
    const u8 offsets[2] = {0x00, 0x40};
    lcd_cmd(0x80 | (offsets[row] + col));
}
void welcome(){
	int j;
	int i;
	lcd_set_cursor(1,2);
	lcd_print("ALDICO S.A.S");
	lcd_set_cursor(0,0);
	lcd_print("");
	usleep(500000);
    char palabra[] = "Bienvenido";
    char buffer[10];   // máximo "HOLA" + '\0'
    int len = strlen(palabra);

    buffer[0] = '\0';

	for (int i = len - 1; i >= 0; i--) {

	        // Construir buffer desde palabra[i] hasta el final
	        int pos = 0;
	        for (int j = i; j < len; j++) {
	            buffer[pos++] = palabra[j];
	        }
	        buffer[pos] = '\0';   // terminar string

	        lcd_set_cursor(0, 0);
	        lcd_print("                ");  // limpiar fila
	        lcd_set_cursor(0, 0);
	        lcd_print(buffer);             // imprimir resultado

	        usleep(200000); // medio segundo
	    }



    lcd_set_cursor(0,0);
    for (i = 0; i < 16; i++) {
    lcd_print("Bienvenido");
    usleep(200000);

    lcd_set_cursor(0,i);
    lcd_print(" ");
    usleep(1000);

    }}
void lcd_init()
{
    usleep(50000);
    lcd_send_nibble(0x30, 0);
    usleep(4500);
    lcd_send_nibble(0x30, 0);
    usleep(4500);
    lcd_send_nibble(0x20, 0);
    lcd_cmd(0x28);
    lcd_cmd(0x0C);
    lcd_cmd(0x06);
    lcd_cmd(0x01);
    usleep(2000);
}


int writeReg_sensor(u8 reg, u8 value)
{
    u8 data[2] = {reg, value};
    int status;

    status = XIicPs_MasterSendPolled(&Iic, data, 2, QMC5883_ADDR);
    while (XIicPs_BusIsBusy(&Iic));

    return (status == XST_SUCCESS) ? XST_SUCCESS : XST_FAILURE;
}

void mostrar_lectura_magnetometro(int *x, int *y, int *z)
{
    u8 buf[6];
    s16 xx, yy, zz;

    if (QMC_read6(buf) == XST_SUCCESS) {

        // Armar valores
        xx = (buf[1] << 8) | buf[0];
        yy = (buf[3] << 8) | buf[2];
        zz = (buf[5] << 8) | buf[4];

        // ======== RETORNAR VALORES ========
        *x = xx;
        *y = yy;
        *z = zz;

        // ---------- UART ----------
        xil_printf("1,%d,%d,%d\r\n", xx, yy, zz);

        // ---------- Convertir a string ----------
        char sx[8], sy[8], sz[8];
        itoa(xx, sx, 10);
        itoa(yy, sy, 10);
        itoa(zz, sz, 10);

        // ---------- LCD ----------
        lcd_set_cursor(0, 0);
        lcd_print("X:");
        lcd_print(sx);

        lcd_set_cursor(1, 0);
        lcd_print("Y:");
        lcd_print(sy);

        lcd_set_cursor(1, 8);
        lcd_print("Z:");
        lcd_print(sz);

    }
    else {
        xil_printf("ERROR leyendo QMC5883\r\n");
        lcd_set_cursor(0, 0);
        lcd_print("Err lectura    ");

        // Devolver 0 por si falla
        *x = 0;
        *y = 0;
        *z = 0;
    }
}







int readBytes_sensor(u8 reg, u8 *buffer, int len)
{
    int status;

    // Enviar dirección de registro
    status = XIicPs_MasterSendPolled(&Iic, &reg, 1, QMC5883_ADDR);
    while (XIicPs_BusIsBusy(&Iic));
    if (status != XST_SUCCESS)
        return XST_FAILURE;

    // Leer datos
    status = XIicPs_MasterRecvPolled(&Iic, buffer, len, QMC5883_ADDR);
    while (XIicPs_BusIsBusy(&Iic));

    return (status == XST_SUCCESS) ? XST_SUCCESS : XST_FAILURE;
}

u32 leer_teclado(XGpio *GpioVerilog)
{
    // Escribir un 0 en canal 1
    XGpio_DiscreteWrite(GpioVerilog, 1, 0);

    // Leer canal 2
    u32 value = XGpio_DiscreteRead(GpioVerilog, 2);
    value &= 0xF;

    usleep(200200);

    if (value != 0) {
        XGpio_DiscreteWrite(GpioVerilog, 1, 1);
        return value;   // devuelve la tecla presionada
    }

    usleep(20000);

    for (volatile int i = 0; i < 1000000; i++);

    return 0;  // no hay tecla
}


void crear_usuario_y_contrasena(XGpio *teclado)
{
    char usuario[20];
    char contrasena[20];
    int idx = 0;

    // ============================
    //    CAPTURAR USUARIO
    // ============================

    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Crear Usuario:");
    lcd_set_cursor(1,0);

    idx = 0;
    usuario[0] = '\0';

    while (1) {
        u32 tecla = leer_teclado(teclado);
        if (tecla == 0) continue;

        // D = confirmar
        if (tecla == 0xD) {
            usuario[idx] = '\0';
            break;
        }

        if (idx < 19) {
            char c;
            sprintf(&c, "%X", tecla);
            usuario[idx++] = c;
            usuario[idx] = '\0';

            lcd_set_cursor(1,0);
            lcd_print(usuario);
        }

        usleep(150000);
    }

    // ============================
    //    CAPTURAR CONTRASEÑA
    // ============================

    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Crear Pass:");
    lcd_set_cursor(1,0);

    idx = 0;
    contrasena[0] = '\0';

    while (1) {
        u32 tecla = leer_teclado(teclado);
        if (tecla == 0) continue;

        // D = confirmar
        if (tecla == 0xD) {
            contrasena[idx] = '\0';
            break;
        }

        if (idx < 19) {
            char c;
            sprintf(&c, "%X", tecla);
            contrasena[idx++] = c;
            contrasena[idx] = '\0';

            lcd_set_cursor(1,0);
            lcd_print(contrasena);
        }

        usleep(150000);
    }

    // ============================
    //     ENVIAR AL UART
    // ============================

    xil_printf("2,%s,%s\r\n", usuario, contrasena);

    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Guardado!");
    usleep(400000);
}


int comprobar_usuario(XGpio *teclado)
{
    char usuario[20];
    char contrasena[20];
    int idx = 0;

    // ============================
    // CAPTURAR USUARIO
    // ============================
    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Ingrese Usuario:");
    lcd_set_cursor(1,0);

    idx = 0;
    usuario[0] = '\0';

    while (1) {
        u32 tecla = leer_teclado(teclado);
        if (tecla == 0) continue;

        if (tecla == 0xD) {
            usuario[idx] = '\0';
            break;
        }

        if (idx < 19) {
            char c;
            sprintf(&c, "%X", tecla);
            usuario[idx++] = c;
            usuario[idx] = '\0';
            lcd_set_cursor(1,0);
            lcd_print(usuario);
        }
        usleep(150000);
    }

    // ============================
    // CAPTURAR CONTRASEÑA
    // ============================
    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Ingrese Clave:");
    lcd_set_cursor(1,0);

    idx = 0;
    contrasena[0] = '\0';

    while (1) {
        u32 tecla = leer_teclado(teclado);
        if (tecla == 0) continue;

        if (tecla == 0xD) {
            contrasena[idx] = '\0';
            break;
        }

        if (idx < 19) {
            char c;
            sprintf(&c, "%X", tecla);
            contrasena[idx++] = c;
            contrasena[idx] = '\0';
            lcd_set_cursor(1,0);
            lcd_print(contrasena);
        }

        usleep(150000);
    }

    // ============================
    // ENVIAR LOGIN A PYTHON
    // ============================
    xil_printf("3,%s,%s\n", usuario, contrasena);

    // ============================
    // ESPERAR RESPUESTA LIMPIA
    // ============================
    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Verificando...");

    char respuesta = 0;

    // ---> IGNORAR '\n' y '\r' !!!
    while (respuesta == 0 || respuesta == '\n' || respuesta == '\r') {
        respuesta = inbyte();
    }

    lcd_clear();

    if (respuesta == 'T') {
        lcd_set_cursor(0,0);
        lcd_print("Acceso Correcto");
        usleep(1500000);
        return 1;
    } else {
        lcd_set_cursor(0,0);
        lcd_print("Acceso Denegado");
        usleep(1500000);
        return 0;
    }
}





int mostrar_menu(XGpio *teclado)
{
    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("1) Registrarse");
    lcd_set_cursor(1,0);
    lcd_print("2) Iniciar Sesion");

    while (1)
    {
        u32 tecla = leer_teclado(teclado);

        if (tecla == 0)
            continue;

        // TU TECLADO ENTREGA HEXA (1,2,3,... A,B,C,D)
        // Queremos SOLO 1 o 2
        if (tecla == 0x1)
            return 1;
        if (tecla == 0x2)
            return 2;


        usleep(150000);
    }
}



int menu_con_login(XGpio *teclado)
{
    const char *opciones[] = {
        " Medir Campo Mag",
        " Prueba Seguridad",
        " Info Usuario",
        " Cambiar Clave",
        " Ultimo Incidente",
        " Cerrar Sesion"
    };

    int total = 6;
    int pos = 0;

    while (1)
    {
        // ============================
        // MOSTRAR MENU
        // ============================
        lcd_clear();

        lcd_set_cursor(0,0);
        lcd_print(">");
        lcd_print(opciones[pos]);

        lcd_set_cursor(1,0);
        if (pos + 1 < total)
            lcd_print(opciones[pos + 1]);
        else
            lcd_print("                ");

        // ============================
        // LEER TECLA
        // ============================
        u32 tecla = leer_teclado(teclado);

        if (tecla == 0) {
            usleep(80000);

        }

        // Flecha arriba
        if (tecla == 0xA) {     // A
            if (pos > 0)
                pos--;
        }

        // Flecha abajo
        else if (tecla == 0xB) {   // B
            if (pos < total - 1)
                pos++;
        }

        // Seleccionar
        else if (tecla == 0xD) {   // D
            return pos + 1;
        }

        usleep(150000); // parecido al menu simple
    }
}
#include <stdio.h>
#include <string.h>
#include "xgpio.h"
#include "Funciones.h"

// Cambiar contraseña de un usuario
int cambiar_contrasena(XGpio *teclado)
{
    char usuario[20];
    char nueva_contrasena[20];
    int idx;

    // ============================
    // Seleccionar usuario
    // ============================
    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Usuario a cambiar:");
    lcd_set_cursor(1,0);

    idx = 0;
    usuario[0] = '\0';

    while (1) {
        u32 tecla = leer_teclado(teclado);
        if (tecla == 0) continue;

        // D = confirmar
        if (tecla == 0xD) {
            usuario[idx] = '\0';
            break;
        }

        if (idx < 19) {
            char c;
            sprintf(&c, "%X", tecla);
            usuario[idx++] = c;
            usuario[idx] = '\0';

            lcd_set_cursor(1,0);
            lcd_print(usuario);
        }

        usleep(150000);
    }

    // ============================
    // Ingresar nueva contraseña
    // ============================
    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Nueva Clave:");
    lcd_set_cursor(1,0);

    idx = 0;
    nueva_contrasena[0] = '\0';

    while (1) {
        u32 tecla = leer_teclado(teclado);
        if (tecla == 0) continue;

        // D = confirmar
        if (tecla == 0xD) {
            nueva_contrasena[idx] = '\0';
            break;
        }

        if (idx < 19) {
            char c;
            sprintf(&c, "%X", tecla);
            nueva_contrasena[idx++] = c;
            nueva_contrasena[idx] = '\0';

            lcd_set_cursor(1,0);
            lcd_print(nueva_contrasena);
        }

        usleep(150000);
    }

    // ============================
    // Enviar UART a Python
    // ============================
    xil_printf("5,%s,%s\n", usuario, nueva_contrasena);

    // ============================
    // Esperar respuesta 'T' o 'F'
    // ============================
    char respuesta = 0;
    lcd_clear();
    lcd_set_cursor(0,0);
    lcd_print("Procesando...");

    while (respuesta == 0 || respuesta == '\n' || respuesta == '\r') {
        respuesta = inbyte();  // inbyte() debe leer desde UART
    }

    lcd_clear();
    if (respuesta == 'T') {
        lcd_set_cursor(0,0);
        lcd_print("Cambio Exitoso");
        usleep(1500000);
        return 1; // Éxito
    } else {
        lcd_set_cursor(0,0);
        lcd_print("Cambio Fallido");
        usleep(1500000);
        return 0; // Falla
    }
}
