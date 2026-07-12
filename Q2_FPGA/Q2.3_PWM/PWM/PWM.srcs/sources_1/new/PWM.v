`timescale 1ns / 1ps

module PWM(
	input clk,
	input rst,
	input [3:0]duty_in,
	output reg pwm_out
);

	reg [3:0] counter;
	
	always@ (posedge clk or posedge rst) begin
	
		if (rst) begin
			counter <= 0;
			pwm_out <= 0;
		end 
		else begin
		
			if (counter == 9 )			
				counter <= 0;
			else
				counter <= counter + 1 ;
				
			if(counter < duty_in )
				pwm_out <= 1;
			else
				pwm_out <= 0;
		end
	end
endmodule
