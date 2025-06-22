create database MovieVault;
use MovieVault;

create table Filmes (
	id int auto_increment primary key,
    nome varchar(255) not null,
    ano year not null,
    genero varchar(50) not null,
    sinopse text not null,
    poster varchar(255) not null
);