CREATE TABLE usuarios (
  user_id serial,
  user_name varchar(20) NOT NULL,
  password varchar(20) NOT NULL,
  PRIMARY KEY (user_id)
);

CREATE TABLE frases (
  frase_id serial,
  user_id integer NOT NULL,
  frase varchar(100) NOT NULL,
  PRIMARY KEY (frase_id)
);
