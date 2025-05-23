from typing import Literal, Optional, Union

from .models import DAILY_DATA, DAILY_DATA_KEYS, MONTH_AVG, REAL_TIME, REAL_TIME_KEYS, real_time_fields

class Stock:
    """股票"""
    KEYS = Literal[REAL_TIME_KEYS,"每日交易資料", "月平均資料" ]
    
    

    def __init__(self, stock_no: str=None):
        """
        建立 Stock 物件。

        參數:
            stock_no (str): 股票代號，若為 None 則不初始化資料。
        
        引發:
            ValueError: 若資料格式錯誤或缺少必要欄位。
        """
        if not stock_no:
            raise ValueError("無效的原始資料")

        self.__no = stock_no
        self.__data: dict[Stock.KEYS, str | list[dict[str, str]]] = {}
        
    def __str__(self) -> str:
        return f"{self.__no}: {self.get('股票簡稱')[0] or '無名稱'}"
    
    def set_data(
        self,
        daily_data: Optional[DAILY_DATA] = None,
        real_time_data: Optional[REAL_TIME] = None,
        month_avg_data: Optional[MONTH_AVG] = None
        ) -> None:
        """
        設定股票資料。

        參數:
            real_time_data (Optional[REAL_TIME]): 即時資料，格式為 {欄位名稱: 欄位值}。
            daily_data (Optional[DAILY_DATA]): 每日交易資料，格式為 [日期, 開盤價, 最高價, 最低價, 收盤價, 成交股數, 成交金額]。
            month_avg_data (Optional[MONTH_AVG]): 月平均資料，格式為 [月份, 平均價]。
        
        """
        if real_time_data:
            for key, symbol in real_time_fields.items():
                if symbol in real_time_data:
                    self.__data[key] = real_time_data[symbol]
        
        if daily_data:
            self.__data["每日交易資料"] = [
                dict(zip(daily_data["fields"], row)) for row in daily_data["data"]
            ]
                    
        if month_avg_data:
            self.__data["月平均資料"] = [{"月份": date, "平均收盤價": avg} for date, avg in month_avg_data.items()]
        
    def get_data(self) -> dict:
        return self.__data

    def get_no(self) -> str:
        return self.__no
    
    def get(self, key:KEYS, date_range: Optional[tuple[str, str]] = None) -> list[str|list[dict[DAILY_DATA_KEYS, str]]]:
        if not self.__data:
            return []
        if key not in self.__data:
            raise KeyError(f"無此欄位：{key}")
    
        if key == "每日交易資料":
            if date_range:
                start, end = date_range
                return [[data for data in self.__data["每日交易資料"] if start <= data["日期"] <= end]]
            return [self.__data["每日交易資料"]]
        
        return [self.__data[key]]
    
    
    def daily_field_transform(
        self,
        field: DAILY_DATA_KEYS,
        interval: Literal["day", "month"],
        date_range: Optional[tuple[str, str]] = None
    ) -> Optional[list[list[str,float]]]:
        """
        擷取每日交易資料中指定欄位的資料，並根據時間間隔進行聚合（每日或每月）。

        參數:
            field (DAILY_DATA_KEYS): 欲擷取的欄位，如 "收盤價"。
            interval (Literal["day", "month"]): 時間間隔，日或月。
            date_range (Optional[tuple[str, str]]): 起始與結束日期，格式為 YYYYMMDD。

        回傳:
        Optional[list[list[str,float]]] : 日期與對應的值的列表。
        """
        
        if field == "收盤價" and interval == "month" and "月平均資料" in self.__data:
                return sorted(
                    [[data["月份"], float(data["平均收盤價"])] for data in self.__data["月平均資料"]],
                    key=lambda x: x[0]
                    )   
        
        raw_data: list[dict[DAILY_DATA_KEYS, str]] = self.get("每日交易資料", date_range=date_range)[0]

        # 資料整理與轉換
        sorted_data: list[list[str, float]] = []
        for data in raw_data:
            date = data.get("日期")
            val_str = data.get(field, "")
            try:
                val = float(val_str.replace(",", ""))
                sorted_data.append([date, val])
            except (ValueError, TypeError):
                continue

        if not sorted_data:
            return None
        
        if interval == "month":
            monthly_data: dict[str, list[float]] = {}
            for date, value in sorted_data:
                yyyymm = date[:6]
                monthly_data.setdefault(yyyymm, []).append(value)
            sorted_data = [[yyyymm, sum(values) / len(values)] for yyyymm, values in monthly_data.items()]

        # 資料排序
        sorted_data.sort(key=lambda x: x[0])

        # 聚合資料

        return sorted_data
        
    def kline(
        self,
        date_range: Optional[tuple[str, str]] = None,
    ) -> Optional[list[dict[str, str| float]]]:
        """
        擷取每日交易資料中的 K 線圖所需欄位資料（開、高、低、收），並轉為 float。

        參數:
            date_range (Optional[tuple[str, str]]): 起始與結束日期，格式為 YYYYMMDD。

        回傳:
            Optional[list[dict[str, float]]]: 每筆資料包含 date/open/high/low/close。若無有效資料則回傳 None。
        """
        raw_data: list[dict[DAILY_DATA_KEYS, str]] = self.get("每日交易資料", date_range=date_range)[0]
        result: list[dict[str, float]] = []

        for data in raw_data:
            try:
                result.append({
                    "date": data["日期"],
                    "open": float(data["開盤價"].replace(",", "")),
                    "high": float(data["最高價"].replace(",", "")),
                    "low": float(data["最低價"].replace(",", "")),
                    "close": float(data["收盤價"].replace(",", "")),
                })
            except (ValueError, KeyError, TypeError):
                continue  # 忽略資料格式錯誤的筆數

        if not result:
            return None

        # 按照日期排序
        result.sort(key=lambda x: x["date"])

        return result

