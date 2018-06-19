/* fbinary_1wave.c  Binary event file with 1 wave (but NOT histograms!)
 * (C) 2012, Wojtek Skulski <skulski@skutek.com>
 * FPGA waveforms are written to a file in binary.
 * Reference: http://www.cprogramming.com/tutorial/cfileio.html
 * The AMS0 memory space must be configured 32-bits in kernel.
 *
 *   bfin-linux-uclibc-gcc -Wall -o fbinary_1wave -mfdpic fbinary_1wave.c
 *   cp  fbinary_1wave /home/uclinux/uClinux-dist/romfs/usr/bin
 *   sudo cp fbinary_1wave /mnt/win
 *
 * Pseudocode:
 *    ievent := 0;
 *    DO WHILE ( ievent < nevent)
 *	(* read FPGA status register *)
 *	IF acquisition is not running THEN 
 *	    (* read data *)
 *	    (* write data in binary to file*)
 *	    (* rearm FPGA acquisition*)
 *	    ievent := ievent + 1;
 *	END IF;
 *   END; (* DO WHILE *)
 */
#include <stdio.h>
#include <stdlib.h>
// #include <unistd.h>	/* commented out for future use*/
// #include <string.h>
// #include <errno.h>
// #include <signal.h>
// #include <fcntl.h>
// #include <ctype.h>
// #include <termios.h>
// #include <sys/types.h>
// #include <sys/mman.h>

#include "/opt/uClinux/futils/bitmasks.h"	/*useful bitmasks*/
#include "/opt/uClinux/futils/fpga_4futils.h"	/*FPGA addresses*/
#include "/opt/uClinux/futils/fcommon.c"		/*FPGA utility functions*/  


#define TOO_MANY_EVENTS 100001	/* avoid trashing the disk*/
#define N_SAMPLES 8192		/* waveforms contain 8192 samples*/

#define HISTOGRAM_SIZE 256

static inline unsigned long long read_cycles (void){
  unsigned long long t0;
  asm volatile ("%0=cycles; %H0=cycles2;" : "=d" (t0));
  return t0;
}

int main(int argc, char **argv) {
	unsigned long  nsmpls, nwave, i;
	size_t nsmpls2;			/*nsamples / 2*/
	unsigned long nevts, ievent, ntrials;
	unsigned long  wave_start; 
	unsigned short lo, hi;
	unsigned long  *base_ptr; 	/* +4 pointer math*/ 
	unsigned long  *lptr; 		/* +4 pointer math*/ 
	unsigned long  lword; 
	volatile unsigned long bits;	/* aux variable for bit test*/
	long  run_time_ms;		/* total run time in ms*/
	long long Tstart_lt;
	long long Tstop_lt;
	long long Tstart_dt;
	long long Tstop_dt;
	long long total_livetime;
	long long total_deadtime;
	FILE * fp;
	unsigned long header [N_SAMPLES / 2];	/*local buffer*/
	unsigned int channel[7] = {0,2,3,4,7,8,9};
	/* -----------------------------------------------------------
	 * Tutorial: let's do some in-situ processing. 
	 * We can calculate and then histogram anything we wish.
	 * Here we will benchmark the performance of event processing.
	 * The stop watch with CLK resolution is in the FPGA. 
	 * It counts clock ticks, 10 ns on most BlackVME boards.
	 * ----------------------------------------------------------*/


// argc = 1 when called without any arguments
// argc = 2 when called with one argument
	if(argc < 4) {
	fprintf(stderr, /*  0   1     2      3   */
		"\nUsage:\t%s  nsamples  nevts fname\n"
		"\tnsmpls : samples to read (1 to 8192) \n"
		"\tnevts  : how many events to write \n"
		"\tfname  : file name (e.g., chan0.bin) \n"
		"\tThis program will NOT read histograms! \n"
		"\t[output is binary] \n",
		argv[0]); /* 0 = name of the executable */
		exit(1);
	}
	run_time_ms = Get_milliseconds ();	/* start ms stop watch*/
	fp = fopen(argv[3], "wb");	/*open file in binary write mode*/
	if (fp == NULL) {
	 fprintf(stderr,"Failed to fopen binary event file\n");
	 exit(1);
	}
	nsmpls = strtoul(argv[1], 0, 0); /* how many samples each wave*/
	nevts  = strtoul(argv[2], 0, 0); /* how many events*/

        if ((nevts < 0) || (nevts >= TOO_MANY_EVENTS)) {
	    fprintf(stderr, "Invalid num of events: %ld\n", nevts);
            return 0;
        } /* sanity check: invalid number of events*/

        if ((nsmpls < 0) || (nsmpls > N_SAMPLES)) {
	    fprintf(stderr, "Invalid num of ADC samples: %ld\n", nsmpls);
            return 0;
        } /* sanity check: invalid number of ADC samples*/

        /* wave_start address and pointer to FPGA waveforms */

	// 2015/03/28 can't find the code for FPGA_REVN_REG so
	// commenting it out. and rewording header[2]. -Dev
	//bits = Get_FPGA_any_Register (FPGA_REVN_REG);

	header[0] = nevts;	/*not limited to 64k*/
	header[1] = nsmpls;	/*at most 8k*/
	// header[2] = bits;	/*firmware revision number*/
	header[2] = nsmpls;
	header[3] = 0xABCDBEEF;	/*pattern word to decipher byte order*/
	fwrite (header, sizeof(header[0]), 4, fp);

	/* prepare the histogram: zero it*/

	/* **************** */
	/* BEGIN OUTER LOOP */
	/* **************** */
	ievent  = 0;
	ntrials = 0;	/*how many times did we try the FPGA?*/
	Tstart_lt = read_cycles();
	total_livetime = 0;

	while ( ievent < nevts) {

        /* ------------------------------------------------
	 * Check if FPGA is running the waveform capture. 
	 * If so then do not attempt reading the waveform. 
	 * ------------------------------------------------*/
	ntrials ++;
	bits = FPGA_is_running();  /*1 == running; 0 == not running*/


        if ( bits == 0 ) {

		Tstop_lt = read_cycles();
		total_livetime = total_livetime + (Tstop_lt-Tstart_lt);
		Tstart_dt=read_cycles();
		

		int j;
		for (j=0;j<7;j++){
		/* We have decided only to digitize channels 0,3 & 6 */
		nwave =channel[j];
		/* In this header we tell which wave we will record.*/
		lo = (unsigned short) nwave;
		hi = 0xDEFA;    /*this marker will be seen as FADE in hex*/
		header[0] = lo | (hi << 16);
		fwrite (header, sizeof(header[0]), 1, fp);

		/*Here we say how many samples will follow*/
		lo = (unsigned short) nsmpls;
		hi = 0xEFBE;	/*this marker will be seen as BEEF in hex*/
		header[0] = lo | (hi << 16);
		fwrite (header, sizeof(header[0]), 1, fp);

			wave_start = FPGA_WAVE_START + nwave * FPGA_WAVE_GAP;
			base_ptr   = (unsigned long *) wave_start;
            for (i = 0; i < nsmpls/2; i++) {
                
                lptr = (unsigned long *) (base_ptr + i);
				header[i] = *( lptr);	/* Transfer to local array*/           
            }
	
		fwrite (header, 4, nsmpls/2, fp);

		/* In this header we tell which wave we recorded.*/
		lo = (unsigned short) nwave;
		hi = 0xADDE;;    /*this marker will be seen as DEAD in hex*/
		header[0] = lo | (hi << 16);
		fwrite (header, sizeof(header[0]), 1, fp);
		
		}

		ievent++;
		Tstop_dt = read_cycles();
		total_deadtime = total_deadtime + (Tstop_dt - Tstart_dt);
		printf("%ld,%llu ,%llu , %llu \n", ievent, Tstop_lt, (Tstop_lt-Tstart_lt),(Tstop_dt - Tstart_dt));
		Tstart_lt=read_cycles();StartFPGA_single (); 


	    			/*inc event counter*/
        } /* if FPGA data was waiting */

	} /* end of outer WHILE (loop over events)*/

	/* IGOR trailing commands: display the histogram*/


	 /* Show the run statistics*/
	 run_time_ms = Get_milliseconds () - run_time_ms;	/*total run time*/
	 printf("X // We acquired %ld events\n", nevts);
	 printf("X // Program ran (LiveTime+DeadTime)= %ld ms\n", run_time_ms);
	 printf("%llu,%llu\n",total_livetime,total_deadtime);


	 fflush(stdout);
	 fclose(fp);	/*close the event file*/
	 return 0;
}
