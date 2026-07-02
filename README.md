# Q2-1

核心目標：設計一個有限狀態機，模擬交通號誌燈的運作，讓綠燈、黃燈、紅燈依序自動切換。

流程：定義狀態 ＞ 設計狀態轉換 ＞ 計數器控制 ＞ 模擬驗證 

定義狀態：

GREEN  → 00
YELLOW → 01
RED    → 10

設計狀態轉換：

GREEN（8個時脈）
    ＞
YELLOW（2個時脈）
    ＞
RED（10個時脈）
    ＞
回到 GREEN（循環）

計數器控制：

計數器負責計算每個狀態待了幾個時脈
當計數器達到指定數量 → 切換到下一個狀態
切換後計數器歸零重新計算

模擬驗證：

在 Vivado 執行模擬
觀察波形確認切換時序正確

使用AI的提示詞:

我要先做Q2.1，我用verilog做，我的檔名叫FSM


這部分是給FPGA的輸出嗎


有個地方看不懂output reg [1:0] light這行是寫給甚麼用的


在主程式light起到什麼作用，可以不要它嗎

<img width="1278" height="288" alt="image" src="https://github.com/user-attachments/assets/9eab6fe3-6547-4de6-b433-27c26cbcf880" />
