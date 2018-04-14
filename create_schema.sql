CREATE TABLE race_list_old(
    serial_no SERIAL PRIMARY KEY,
    kaisaibi  TEXT,
    kaijou TEXT,
    no INTEGER,
    name TEXT,
    url TEXT,
    UNIQUE (kaisaibi,kaijou,no)
)
;
CREATE TABLE race_list_old2(
    serial_no SERIAL PRIMARY KEY,
    kaisaibi TEXT,
    kaijou TEXT,
    url TEXT,
    UNIQUE (kaisaibi,kaijou)
)
;
CREATE TABLE odds_list(
    serial_no SERIAL PRIMARY KEY,
    rece_serial INTEGER,
    rank INTEGER,
    no1 INTEGER,
    no2 INTEGER,
    no3 INTEGER,
    odds NUMERIC,
    UNIQUE(rece_serial,rank)
)
;
--DROP TABLE race_list_murao;
CREATE TABLE race_list_murao(
    serial_no SERIAL PRIMARY KEY,
    kaisaibi TEXT,
    youbi TEXT,
    kaijou TEXT,
    nittei TEXT,
    saishu TEXT,
    jikantai TEXT,
    grade TEXT,
    race_no integer,
    series text,
    rank text,
    shubetsu text,
    tenki text,
    fuusoku text, 
    nami text,
    kimarite text,
    no1 integer,
    no2 integer,
    no3 integer,
    haitou3t integer,
    haitou2t integer,
    status integer DEFAULT 0,
    UNIQUE (kaisaibi,kaijou,race_no)
)
;
--DROP TABLE odds_list_murao;
CREATE TABLE odds_list_murao(
    serial_no BIGSERIAL PRIMARY KEY,
    race_serial INTEGER,
    race_id TEXT,
    kachisiki TEXT,
    kumiban text,
    atari integer,
    odds1 NUMERIC,
    ninki1 integer,
    odds5 NUMERIC,
    ninki5 integer,
    UNIQUE(race_id,kachisiki,kumiban)
)
;
-- DROP INDEX odds_list_murao_atari;
-- DROP INDEX odds_list_murao_atari_kachisiki;
-- CREATE INDEX odds_list_murao_atari ON odds_list_murao (atari);
-- CREATE INDEX odds_list_murao_atari_kachisiki ON odds_list_murao (atari,kachisiki);
-- CREATE INDEX odds_list_murao_odds1 ON odds_list_murao (race_id,odds1)
-- DROP VIEW odds_list_3t
CREATE OR REPLACE VIEW odds_list_3t AS SELECT * FROM odds_list_murao WHERE kachisiki='0' AND odds1!=0;

CREATE INDEX odds_list_base0_ninki1 ON odds_list_base0 (ninki1)
CREATE TABLE odds_list_base0 AS SELECT ninki1,MIN(odds1),MAX(odds1) FROM odds_list_koushiki GROUP BY ninki1 ORDER BY ninki1

--DROP TABLE race_result_koushiki;
CREATE TABLE race_result_koushiki(
    serial_no SERIAL PRIMARY KEY,
    race_serial INTEGER,
    race_id TEXT,
    chakujun text,
    tei integer,
    touban integer,
    moter integer,
    boat integer,
    tenji NUMERIC,
    shinnyu NUMERIC,
    starttime text,
    racetime text,
    UNIQUE(race_id,tei)
)
;
-- DROP TABLE race_list_koushiki CASCADE;
CREATE TABLE race_list_koushiki(
    serial_no SERIAL PRIMARY KEY,
    race_id TEXT,
    race_ymd TEXT,
    shime text,
    sumi text default '0',
    kumiban text,
    haitou numeric,
    insert_ts timestamp default now(),
    fill_odds_ts timestamp,
    fill_rslt_ts timestamp,
    UNIQUE(race_id)
)
;
CREATE VIEW race_list_koushiki_view AS
  SELECT serial_no,race_id,shime,sumi,kumiban,haitou,COALESCE(fill_rslt_ts,fill_odds_ts,insert_ts) AS last_upd_ts
  FROM race_list_koushiki ORDER BY race_ymd,shime
;

-- DROP TABLE odds_list_koushiki;
CREATE TABLE odds_list_koushiki(
    serial_no SERIAL PRIMARY KEY,
    race_id text,
    kumiban text,
    atari integer default 0,
    odds1 numeric,
    ninki1 integer,
    odds1e numeric,
    UNIQUE(race_id,kumiban)
)
;

CREATE TABLE holiday(
    serial_no serial primary key,
    ymd date,
    kyujitsu_flg integer,
    UNIQUE(ymd)
)

-- DROP VIEW race_list_atari_kumiban ;
CREATE OR REPLACE VIEW race_list_atari_kumiban_view AS 
SELECT race_id,a.tei||'-'||b.tei||'-'||c.tei AS kumiban FROM 
(SELECT * FROM race_result_koushiki WHERE chakujun IN ('1','01') ) a 
LEFT OUTER JOIN 
(SELECT * FROM race_result_koushiki WHERE chakujun IN ('2','02') ) b USING (race_id) 
LEFT OUTER JOIN 
(SELECT * FROM race_result_koushiki WHERE chakujun IN ('3','03') ) c USING (race_id)
;
race_list_atari_kumiban

  SELECT 
    map,
    POW(999,map/30.),
    COUNT(*),
    SUM(odds1),
    COUNT(*)/3360.*SUM(odds1)/COUNT(*) 
  FROM (
    SELECT * FROM (
        SELECT 
          race_id,
          ninki1,
          FLOOR(LOG(999,odds1)*30) AS map,
          odds1 
        FROM odds_list_koushiki WHERE atari=1 ORDER BY race_id, ninki1 ) a
  ) b WHERE odds1 BETWEEN FLOOR(LOG(999,odds1)*30) AND FLOOR((LOG(999,odds1)*30))+1
  GROUP BY map ORDER BY map

  CREATE OR REPLACE VIEW odds_list_koushiki_atari AS 
  SELECT * FROM odds_list_koushiki WHERE atari=1 AND odds1!=0 ORDER BY race_id;

  SELECT kbn,SUM(ret) FROM (
  SELECT FLOOR(LOG(999,e.odds1)*30) AS kbn,e.odds1/d.cnt AS ret FROM (
    SELECT race_id,COUNT(*) AS cnt,MIN(a.odds1),MAX(a.odds1) 
    FROM odds_list_koushiki a 
    LEFT OUTER JOIN odds_list_koushiki_atari c
    USING(race_id)
    WHERE a.odds1!=0 AND FLOOR(LOG(999,a.odds1)*30) = FLOOR(LOG(999,c.odds1)*30)
    GROUP BY race_id
  ) d LEFT OUTER JOIN odds_list_koushiki_atari e 
  USING(race_id)
  ) f GROUP BY kbn ORDER BY kbn
  ;

  SELECT LOG(999,13.2)

  CREATE TABLE odds_log AS 
    SELECT *,
      CASE WHEN odds1!=0 THEN FLOOR(LOG(999,odds1)*10) ELSE 0 END AS log10, 
      CASE WHEN odds1!=0 THEN FLOOR(LOG(999,odds1)*20) ELSE 0 END AS log20,
      CASE WHEN odds1!=0 THEN FLOOR(LOG(999,odds1)*30) ELSE 0 END AS log30 
    FROM  odds_list_koushiki ORDER BY race_id,ninki1;
  CREATE INDEX odds_log_log10 ON odds_log (log10);
  CREATE INDEX odds_log_log20 ON odds_log (log20);
  CREATE INDEX odds_log_log30 ON odds_log (log30);



CREATE OR REPLACE VIEW odds_list_target AS SELECT * FROM odds_list_koushiki WHERE SUBSTR(race_id,1,6) BETWEEN '201712' AND '201712';
CREATE OR REPLACE VIEW odds_list_test   AS SELECT * FROM odds_list_koushiki WHERE SUBSTR(race_id,1,6) ='201801';
CREATE TABLE odds_list_base00 AS 
    SELECT ninki1,MIN(odds1),MAX(odds1),LOG(MIN(odds1),MAX(odds1)) 
    FROM (SELECT ninki1,odds1 FROM odds_list_target) b GROUP BY ninki1 ORDER BY ninki1
;
DROP TABLE race_dot;
CREATE TABLE race_dot (
    serial_no BIGSERIAL,
    t         integer,
    race_id_0 text,
    race_id_1 text,
    norm_0    numeric,
    norm_1    numeric,
    norm_dot  numeric,
    odds1_0   numeric,
    odds1_1   numeric,
    ninki1_0   integer,
    ninki1_1   integer,
    kumiban_0 text,
    kumiban_1 text,
    dot       numeric
)
norm_dot
CREATE INDEX race_dot_norm_dot ON race_dot (norm_dot)

CREATE VIEW race_list_murao_view AS 
  SELECT 
    kaisaibi||'-'||kaijou||'-'||TRIM(TO_CHAR(race_no,'00')) AS race_id,
    haitou3t AS haitou,
    2 AS sumi,
    '00:00'::TEXT AS shime 
  FROM race_list_murao;

