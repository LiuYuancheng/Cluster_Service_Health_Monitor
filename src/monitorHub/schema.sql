DROP TABLE IF EXISTS evtTimeline;

CREATE TABLE evtTimeline (
    evtId INTEGER PRIMARY KEY NOT NULL,
    evtTitle TEXT,
    updateT TIMESTAMP NOT NULL DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    dayNum INTEGER,
    evtType TEXT,
    teamName TEXT,
    evtState TEXT
);