`timescale 1ns / 1ps


module PWM_tb;

	reg clk;
    reg rst;
    reg [3:0]duty_in;
    wire pwm_out;

    PWM uut (
        .clk(clk),
        .rst(rst),
        .duty_in(duty_in),
        .pwm_out(pwm_out)
    );
	
	initial clk = 0;
	always #5 clk = ~clk;
	
	initial begin
        rst     = 1;
		duty_in = 0;
        #10;
        rst    = 0;
		#5;
        duty_in =3; 
        #100;
		duty_in =7;
		#100
		duty_in =10;
		#100
        $finish;
    end
	
endmodule
