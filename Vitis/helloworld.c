#include "xgpio.h"
#include "xparameters.h"
#include "xil_printf.h"
#include "xiicps.h"
#include "sleep.h"
#include "Funciones.h"

extern XIicPs Iic;

#define I2C_DEVICE_ID        XPAR_XIICPS_0_DEVICE_ID
#define QMC5883_ADDR         0x0D

#define GPIO_VERILOG_ID      XPAR_AXI_GPIO_2_DEVICE_ID
#define GPIO_BUZZER          XPAR_AXI_GPIO_1_DEVICE_ID

#define VERILOG_CHANNEL      1


// ---------------------------------------------------------------------
//   MENÚ SIN LOGIN
// ---------------------------------------------------------------------


// ---------------------------------------------------------------------
//   MENÚ PRINCIPAL
// ---------------------------------------------------------------------


// =====================================================================
//                                MAIN
// =====================================================================
int main() {

    XGpio GpioVerilog;
    XGpio buzzer_verilog;

    // Inicializar buzzer
    XGpio_Initialize(&buzzer_verilog, GPIO_BUZZER);
    XGpio_SetDataDirection(&buzzer_verilog, VERILOG_CHANNEL, 0x00000000);

    // Inicializar GPIO teclado (entrada)
    XGpio_Initialize(&GpioVerilog, GPIO_VERILOG_ID);
    XGpio_SetDataDirection(&GpioVerilog, 1, 0xFFFFFFFF);

    // I2C
    XIicPs_Config *Cfg = XIicPs_LookupConfig(I2C_DEVICE_ID);
    XIicPs_CfgInitialize(&Iic, Cfg, Cfg->BaseAddress);
    XIicPs_SetSClk(&Iic, 100000);

    // LCD
    lcd_init();
    lcd_set_brightness(300);

    QMC_init();

    int logged = 0;


    // BUCLE PRINCIPAL
    while (1)
    {
        // ------------------------------------------------------
        //                      LOGIN / REGISTRO
        // ------------------------------------------------------
        if (!logged )
        {
            int opcion = mostrar_menu(&GpioVerilog);

            if (opcion == 1)
                crear_usuario_y_contrasena(&GpioVerilog);

            else if (opcion == 2)
                logged = comprobar_usuario(&GpioVerilog);

            continue; //  volver a menú login
        }


        // ------------------------------------------------------
        //                  MENU YA LOGEADO
        // ------------------------------------------------------
        int seleccion = menu_con_login(&GpioVerilog);

        // 1) Medir sensor
        if (seleccion == 1)
        {
        	lcd_clear();

            while (1)
            {
                int x, y, z;


                mostrar_lectura_magnetometro(&x, &y, &z);
                u32 t = leer_teclado(&GpioVerilog);

                if(x > 5000 || x < 200 || y > 5000 || y < 200 || z > 5000 || z < 200){
                	lcd_clear();
                	lcd_print("PELIGRO");
                	usleep(2000000);
                    lcd_clear();
                	XGpio_DiscreteWrite(&buzzer_verilog, 1, 1);
                }
                if(t == 0x2){

                	XGpio_DiscreteWrite(&buzzer_verilog, 1, 0);

                }


                if (t == 0xA) break;
                usleep(200000);
            }
        }

        // 2) BUZZER ON
        else if (seleccion == 2)
        {
            XGpio_DiscreteWrite(&buzzer_verilog, 1, 1);
            lcd_clear();
            lcd_print("BUZZER ON");
        	usleep(1000000);
        	XGpio_DiscreteWrite(&buzzer_verilog, 1, 0);
        }

        //Cambiar contraseña
        else if (seleccion == 3)
        {
            XGpio_DiscreteWrite(&buzzer_verilog, 1, 0);
        }

        // 4) Nuevo user
        else if (seleccion == 4)
        {
         cambiar_contrasena(&GpioVerilog);

        }

        // 5) Cerrar sesión
        else if (seleccion == 5)
        {

            lcd_clear();
            lcd_print("Sesion cerrada");
            usleep(800000000);
            continue;
        }
    }

    return 0;
}
