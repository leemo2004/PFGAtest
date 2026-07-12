`timescale 1ns / 1ps
module CRC5_RNG_tb;

    reg clk;
    reg rst;
    reg enable;
    wire [1:0] rand_out;

    // 實例化主模組
    CRC5_RNG uut (
        .clk(clk),
        .rst(rst),
        .enable(enable),
        .rand_out(rand_out)
    );

    // 時脈產生（週期 = 10ns）
    initial clk = 0;
    always #5 clk = ~clk;

    // 測試流程
    initial begin
        rst    = 1;
        enable = 0;
        #10;
        rst    = 0;
        enable = 1;  // 開始產生隨機數
        #100;        // 模擬 10 個時脈
        enable = 0;
        #20;
        $finish;
    end

    // 顯示輸出
    initial begin
        $monitor("Time=%0t | enable=%b | rand_out=%0d", 
                  $time, enable, rand_out);
    end

endmodule