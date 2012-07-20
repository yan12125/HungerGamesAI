
	/*******************************************
	 **                                       **
	 **     2012 臺大電機營 HUNGER GAME       **
	 **      　　   進階程式實驗 3            **
	 **                                       **
	 *******************************************/
	 
/*
說明：
	透過上一題，我們對map這個陣列的兩個屬性有了認識。現在，我們要進一步使用
	empty這個屬性，來使玩家不會隨意穿越障礙物。
	
	near這個函數接收三個參數，分別是玩家的中心位置X, Y，以及玩家圖示的
	二分之一邊長halfSide。
	
	我們定義check這個array，代表要檢查的八個點。
	
	「當這八個點任何一點所在的那格不為空 (即，該格empty為false)，函數回傳值
	  true。若八點所在之格的empty均為true，則函數回傳值為false。」
	
	譬如說，左上角這一點的寫法可以是
	check[0] = gridCalc( X - halfSide, Y - halfSide);
	正上方則為
	check[1] = gridCalc( X , Y - halfSide);
	
	gridCalc是用來算出各點所在之格的函式。
	所以若我想知道左上角是否為false，我可以詢問map[ check[0] ].empty===false
	請善用邏輯運算子！
	「『只要有一個』是false，那就回傳true。」
	
	0     1     2
	↓     ↓     ↓
    ┌───────────┐ 
	│　　　　 　│
	│　　　 　　│
3 → │　　 .     │ ← 4
	│　 (X,Y) 　│
    │　　　 　　│
	└───────────┘ 
	↑     ↑     ↑
	5     6     7
*/
	 
function near(X, Y, halfSide) {
	var check = [];
    check[0] = gridCalc(X - halfSide, Y - halfSide);
	check[1] = gridCalc(X, Y - halfSide);
    check[2] = gridCalc(X + halfSide, Y - halfSide);
    check[3] = gridCalc(X - halfSide, Y);
	check[4] = gridCalc(X + halfSide, Y);
	check[5] = gridCalc(X - halfSide, Y + halfSide);
	check[6] = gridCalc(X, Y + halfSide);
	check[7] = gridCalc(X + halfSide, Y + halfSide);
    for(var i=0;i<8;i++)
		if(!map[ check[i] ].empty)
			return true;
	return false;
}