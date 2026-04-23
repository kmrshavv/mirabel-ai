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
INSERT INTO users VALUES(2,'test_user',NULL,'2026-04-23 18:37:34.008186','{}',0);
INSERT INTO users VALUES(3,'rishav',NULL,'2026-04-23 18:38:26.557189','{}',0);
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
INSERT INTO conversations VALUES(1,3,'My First Chat','2026-04-23 18:38:26.568949','2026-04-23 18:38:26.596003','llama3.2:3b');
INSERT INTO conversations VALUES(2,2,'Test Conversation','2026-04-23 18:39:51.110311','2026-04-23 18:39:51.138997','llama3.2:3b');
CREATE TABLE messages (
	id INTEGER NOT NULL, 
	conversation_id INTEGER, 
	role VARCHAR, 
	content TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);
INSERT INTO messages VALUES(1,1,'user','Hello! This is a test message.','2026-04-23 18:38:26.579756');
INSERT INTO messages VALUES(2,1,'assistant','Hi! I''m Mirabel. Nice to meet you!','2026-04-23 18:38:26.594817');
INSERT INTO messages VALUES(3,2,'user','Hello AI!','2026-04-23 18:39:51.122837');
INSERT INTO messages VALUES(4,2,'assistant','Hello Human!','2026-04-23 18:39:51.138284');
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_model_stats_id ON model_stats (id);
CREATE INDEX ix_conversations_id ON conversations (id);
CREATE INDEX ix_messages_id ON messages (id);
COMMIT;
