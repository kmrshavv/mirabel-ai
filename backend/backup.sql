PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR, 
	email VARCHAR, 
	created_at DATETIME, 
	preferences TEXT, 
	total_conversations INTEGER, 
	PRIMARY KEY (id)
);
INSERT INTO users VALUES(1,'default_user',NULL,'2026-04-23 18:36:30.875536','{}',0);
CREATE TABLE model_stats (
	id INTEGER NOT NULL, 
	model_name VARCHAR, 
	total_calls INTEGER, 
	total_tokens INTEGER, 
	avg_response_time INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (model_name)
);
CREATE TABLE conversations (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	title VARCHAR, 
	created_at DATETIME, 
	updated_at DATETIME, 
	model_used VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE messages (
	id INTEGER NOT NULL, 
	conversation_id INTEGER, 
	role VARCHAR, 
	content TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_model_stats_id ON model_stats (id);
CREATE INDEX ix_conversations_id ON conversations (id);
CREATE INDEX ix_messages_id ON messages (id);
COMMIT;
