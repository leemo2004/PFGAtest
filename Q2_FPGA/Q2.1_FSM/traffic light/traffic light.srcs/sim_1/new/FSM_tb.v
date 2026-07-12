`timescale 1ns / 1ps
module FSM_tb;

    reg clk;
    reg rst;
    wire [1:0] light;

    // 實例化主模組
    FSM uut (
        .clk(clk),
        .rst(rst),
        .light(light)
    );

    // 時脈產生（週期 = 10ns）
    initial clk = 0;
    always #5 clk = ~clk;

    // 測試流程
    initial begin
        rst = 1;
        #10;
        rst = 0;
        #500;  // 模擬足夠長的時間觀察多個週期
        $finish;
    end

    // 顯示狀態
    initial begin
        $monitor("Time=%0t | light=%b (%s)", 
                  $time, light,
                  (light == 2'b00) ? "GREEN" :
                  (light == 2'b01) ? "YELLOW" : "RED");
    end

endmodule