from datetime import datetime

class DateUtil:
    @staticmethod
    def roc_to_ad(roc: str, output_format: str = "%Y%m%d") -> str:
        """
        將民國日期字串（如 '114/04/15'）轉換為西元日期字串（如 '20250415'）。
        
        參數:
            roc (str): 民國日期字串，格式為 'YYY/MM/DD'。
            output_format (str): 輸出的日期格式（預設為 '%Y%m%d'）。
        
        回傳:
            str: 轉換後的西元日期字串。
        """
        try:
            y, m, d = map(int, roc.split('/'))
            return datetime(y+1911, m, d).strftime(output_format)
        except (ValueError, TypeError) as e:
            raise ValueError(f"無法轉換民國日期：{roc}，錯誤：{e}")
        
    @staticmethod
    def ad_to_roc(ad: str, fmt="%Y%m%d") -> str:
        """
        將西元日期字串（如 '20250415') 轉換為民國日期字串（如 '114/04/15'）。
        
        參數:
            ad (str): 西元日期字串，格式為 'YYYYMMDD'。
            fmt (str): 輸出的日期格式（預設為 '%Y%m%d'）。
        
        回傳:
            str: 轉換後的民國日期字串。
        """
        try:
            dt = datetime.strptime(ad, fmt)
            return f"{dt.year - 1911:03}/{dt.month:02}/{dt.day:02}"
        except (ValueError, TypeError) as e:
            raise ValueError(f"無法轉換西元日期：{ad}，錯誤：{e}")
        
    @staticmethod
    def month_range(start: str, end: str) -> list[str]:
        """
        從起訖日期（格式為 'YYYYMMDD'）產生每月第一天的字串清單。

        例如:
            start = '20210101', end = '20210315'
            回傳 = ['20210101', '20210201', '20210301']

        參數:
            start (str): 起始日期，格式為 'YYYYMMDD'。
            end (str): 結束日期，格式為 'YYYYMMDD'。

        回傳:
            list[str]: 每月第一天日期的字串清單。
        """
        try:
            start_dt = datetime.strptime(start, "%Y%m%d").replace(day=1)
            end_dt = datetime.strptime(end, "%Y%m%d").replace(day=1)

            result: list[str] = []
            while start_dt <= end_dt:
                result.append(start_dt.strftime("%Y%m01"))
                # 換下個月
                year, month = start_dt.year + (start_dt.month // 12), (start_dt.month % 12) + 1
                start_dt = start_dt.replace(year=year, month=month)

            return result
        except (ValueError, TypeError) as e:
            raise ValueError(f"無法產生月份範圍：{start} ~ {end}，錯誤：{e}")
    
if __name__ == "__main__":
    print(DateUtil.roc_to_ad('114/04/15')) 
