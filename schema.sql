-- 三民書局暢銷總榜：一天、一個排名，一列
CREATE TABLE IF NOT EXISTS books (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  rank_date  DATE         NOT NULL,             -- 哪一天的排行榜
  rank_no    INT          NOT NULL,             -- 第幾名
  title      VARCHAR(300) NOT NULL,             -- 書名
  author     VARCHAR(300) NOT NULL DEFAULT '',  -- 作者
  publisher  VARCHAR(200) NOT NULL DEFAULT '',  -- 出版社
  url        VARCHAR(300) NOT NULL,             -- 書的網址
  UNIQUE KEY uk_day_rank (rank_date, rank_no)  -- 同一天重跑不會多一份
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
