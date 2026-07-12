`timescale 1ns / 1ps

module FSM(
    input clk,
    input rst,
    output reg [1:0] light  // 00=Green, 01=Yellow, 10=Red
);

    // 狀態定義
    parameter GREEN  = 2'b00;
    parameter YELLOW = 2'b01;
    parameter RED    = 2'b10;

    reg [1:0] state;
    reg [3:0] counter;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state   <= GREEN;
            counter <= 0;
            light   <= GREEN;
        end else begin
            case (state)
                GREEN: begin
                    light <= GREEN;
                    if (counter == 7) begin  // 8 clks (0~7)
                        state   <= YELLOW;
                        counter <= 0;
                    end else begin
                        counter <= counter + 1;
                    end
                end

                YELLOW: begin
                    light <= YELLOW;
                    if (counter == 1) begin  // 2 clks (0~1)
                        state   <= RED;
                        counter <= 0;
                    end else begin
                        counter <= counter + 1;
                    end
                end

                RED: begin
                    light <= RED;
                    if (counter == 9) begin  // 10 clks (0~9)
                        state   <= GREEN;
                        counter <= 0;
                    end else begin
                        counter <= counter + 1;
                    end
                end

                default: begin
                    state   <= GREEN;
                    counter <= 0;
                end
            endcase
        end
    end

endmodule