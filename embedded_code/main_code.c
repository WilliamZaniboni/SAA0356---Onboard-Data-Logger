#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <signal.h>
#include <rc/mpu.h>
#include <rc/time.h>
#include <sys/socket.h>
#include <arpa/inet.h>

// bus for Robotics Cape and BeagleboneBlue is 2, interrupt pin is on gpio3.21
// change these for your platform
#define I2C_BUS 2
#define GPIO_INT_PIN_CHIP 3
#define GPIO_INT_PIN_PIN  21

// Global Variables
static int running = 0;
static int show_good_news = 0;
static rc_mpu_data_t data;
static int sock;
static int counter;

// local functions
static void __print_usage(void);
static void __print_data(void);

static void __print_usage(void)
{
	printf("\n Opcoes\n");
	printf("-r {rate}	Configura a taxa de amostragem em HZ (padrao 100)\n");
	printf("		Taxa de amostragem deve ser um divisor de 200\n");
	printf("-j		Teste de instalacao\n");
	printf("-h		Mostra informacoes de ajuda\n\n");

	return;
}

//Função passado por ponteiro para ser chamada toda vez que houver leitura da IMU
static void __print_data(void){
	if(show_good_news == 1){
		printf("Deu tudo certo! =)\n");
		return;

	}

	char *message = (char *)calloc(50, sizeof(char));
	printf("\r");

	sprintf(message, "%.2lf/%.2f/%.2f/%.2f", 
		((double)counter++/10),
			data.dmp_TaitBryan[TB_PITCH_X], 
			data.dmp_TaitBryan[TB_ROLL_Y],
			data.dmp_TaitBryan[TB_YAW_Z]);

	printf("%s | len : %d\n", message, strlen(message));
	if( send(sock , message , strlen(message), 0) < 0){
		puts("Falha no envio");
		return;
	}
	memset(message, 0, 50);
	recv(sock, message, sizeof(message), 0);
	free(message);
	fflush(stdout);
	return;
}

// Possibilita detectar o ctrl-c
static void __signal_handler(__attribute__ ((unused)) int dummy){
	running=0;
	return;
}



int main(int argc, char *argv[])
{
	int c, sample_rate;
	struct sockaddr_in server;

	//Configura os periféricos da BBBlue como padrão
	rc_mpu_config_t conf = rc_mpu_default_config();
	conf.i2c_bus = I2C_BUS;
	conf.gpio_interrupt_pin_chip = GPIO_INT_PIN_CHIP;
	conf.gpio_interrupt_pin = GPIO_INT_PIN_PIN;

	// Parsing dos argumentos
	opterr = 0;
	while ((c=getopt(argc, argv, "r:tjulkm:h"))!=-1 && argc>1){
		switch (c){
		case 'r': // Determinar a taxa de amostragem a ser utilizada
			sample_rate = atoi(optarg);
			if(sample_rate>200 || sample_rate<4){
				printf("sample_rate must be between 4 & 200");
				return -1;
			}
			conf.dmp_sample_rate = sample_rate;
			break;
		case 'j': // Mostra que a instalação deu certo
			show_good_news = 1;
			break;
		case 'h': // Mostra como utilzar o sistema
			__print_usage();
			return -1;
			break;
		default:
			printf("opt: %c\n",c);
			printf("Argumento invalido\n");
			__print_usage();
			return -1;
			break;
		}
	}

	if(show_good_news == 1){
		__print_data();
		return 0;
	}

	//Criando o socket ==============================================================
	sock = socket(AF_INET , SOCK_STREAM , 0);
	if (sock == -1){ printf("Não foi possível criar o socket"); }
	puts("Socket criado!\n");
	
	server.sin_addr.s_addr = inet_addr("192.168.7.1");
	server.sin_family = AF_INET;
	server.sin_port = htons( 8888 );

	if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0){ 
		perror("Falha ao conectar!\n"); return 1;
	}
	puts("Conectado!\n");
	//===============================================================================
	
	signal(SIGINT, __signal_handler);
	running = 1;

	// Configurando a IMU e o sistema para operação em dmp interrupt
	if(rc_mpu_initialize_dmp(&data, conf)){
		printf("rc_mpu_initialize_failed\n");
		return -1;
	}
	//Atribui um ponteiro de função para lidar com a interrupção - "callbacks"
	rc_mpu_set_dmp_callback(&__print_data);
	
	//Somente esperando, a execução do sistema ocorre via interrupção
	while(running)	rc_usleep(100000);

	// Encerrando o sistema
	close(sock);
	rc_mpu_power_off();
	fflush(stdout);
	return 0;
}

