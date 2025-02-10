pragma foreign_keys = on;

create table Alien1(
    x not null,
    y not null,
    z,
    primary key(x, y));

create table Alien2(
    i not null,
    j not null,
    k,
    primary key(i, j));

create table Native(
    a not null primary key,

    b not null,
    c not null,

    e not null,
    f not null,
    foreign key (b, c) references Alien1,
    -- foreign key (b, c) references Alien1(x, y),
    foreign key (e, f) references Alien2);
    -- foreign key (e, f) references Alien2(i, j));
