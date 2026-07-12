`timescale 1ns / 1ps
module CRC5_RNG(
    input clk,
    input rst,
    input enable,        
    output reg [1:0] rand_out  // è¼¸å‡º 0~3
);

    reg [4:0] lfsr;  // 5ä½å?? LFSR

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            lfsr     <= 5'b10001;  // ??å?‹ç¨®å­ï?ˆä?å¯?‚º0ï¼?
            rand_out <= 0;
        end else if (enable) begin
            // CRC5 å¤šé?…å?ï?šx^5 + x^3 + 1
            lfsr <= {lfsr[3:0], lfsr[4] ^ lfsr[2]};
            rand_out <= lfsr[1:0];  // ??–ä?å…©ä½å?ƒå?—åˆ° 0~3
        end
    end
endmodule