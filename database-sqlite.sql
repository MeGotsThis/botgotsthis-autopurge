CREATE TABLE auto_purge (
    broadcaster VARCHAR NOT NULL,
    twitchUser VARCHAR NOT NULL,
    stopcommands BOOLEAN NOT NULL,
    PRIMARY KEY (broadcaster, twitchUser)
);
