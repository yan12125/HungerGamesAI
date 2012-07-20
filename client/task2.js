
	/*******************************************
	 **                                       **
	 **     2012 臺大電機營 HUNGER GAME       **
	 **      　　   進階程式實驗 2            **
	 **                                       **
	 *******************************************/

/*
說明：
	map是儲存地圖中各格內容物、及規範玩家穿越的陣列。
	譬如說，map[i](第i格)的empty屬性 (map[i].type)若為 true ，則玩家可穿越。
	否則 ( false ) 的話，玩家將被阻擋在這格前。
	
	map[i].type (type屬性)則用一個字串儲存這格實際的內容。對應如下
	
		'vwall'  木箱
		'nvwall' 磚牆
		'bomb'   炸彈
		'tool'   道具
		'empty'  空無一物
	
	你可能已經猜到，'tool'和'empty'對應到的empty屬性是true，其他則為false
	
	現在，fireInTheHole函式接收參數pos，是炸彈剛剛爆炸了的位置。請你將map[i]
	的兩個屬性type和empty，從原始有炸彈的狀態，調整為「空無一物」。
	最後再呼叫pos這個參數，繼續呼叫bombRemove函式，來將畫面上的炸彈圖示清除。
*/

/************************************************
					請在此作答
************************************************/
function fireInTheHole(pos){
	map[pos].type = 'empty';
    map[pos].empty = true;
    bombRemove(pos);
	return;
}

function bombRemove(pos){
	grids[pos].classList.remove('bomb');
	return;
}

/************************************************
					作答結束
************************************************/	