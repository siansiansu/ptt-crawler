# PTT 爬蟲

![./gif/demo.gif](./gif/demo.gif)

## 使用方式

```bash
pip install -r requirements.txt
python ./main.py [開始時間] [結束時間] [下載目錄] [關鍵字]
```


## 範例


```bash
cd Desktop # 切換到桌面
python ./main.py 2023-07-01 2023-07-12 關於疫情的文章 疫情,校正回歸,高端,超前部署,新冠,確診
python ./main.py 2023-07-01 2023-07-12 關於選舉的文章 大選,六都,選舉,投票,選票
```

## 注意
- 如果使用不同的關鍵字，下載的文章並不相同，建議指定不同的下載目錄。
- 文章如果沒有日期，以 99-99-99 表示。
