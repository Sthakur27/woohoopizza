--
-- Example setup file for a web database project.
--

create table User(
    id int not null auto_increment primary key,
    email varchar(255) not null,
	password_hash varchar(255) not null,
	phone_number varchar(255) not null
);

create table FoodBaseData(
	id int not null primary key,
	base_calories float,
	base_price float
);

create table Pizza(
    id int not null auto_increment primary key,
	base_data_id int not null,
	pizza_size int,
	FOREIGN KEY (base_data_id) REFERENCES FoodBaseData(id)
);

create table Topping(
    id int not null auto_increment primary key,
	base_data_id int not null,
	name varchar(255) not null,
	FOREIGN KEY (base_data_id) REFERENCES FoodBaseData(id)
);

create table Drink(
    id int not null auto_increment primary key,
	base_data_id int not null,
	name varchar(255) not null,
	FOREIGN KEY (base_data_id) REFERENCES FoodBaseData(id)
);

create table BreadStick(
    id int not null auto_increment primary key,
	base_data_id int not null,
	name varchar(255) not null,
	FOREIGN KEY (base_data_id) REFERENCES FoodBaseData(id)
);

create table UserOrder(
    id int not null auto_increment primary key,
    orderstatus varchar(255) not null,
	user_id int not null,
	placed_on datetime,
	notes varchar(5000),
	FOREIGN KEY (user_id) REFERENCES User(id)
);

create table Pizza_Order(
    id int not null auto_increment primary key,
	pizza_id int not null,
	order_id int not null,
	quantity int not null,
	FOREIGN KEY (pizza_id) REFERENCES Pizza(id),
	FOREIGN KEY (order_id) REFERENCES UserOrder(id)
);

create table Pizza_Topping(
	id int not null auto_increment primary key,
	pizza_order_id int not null,
	topping_id int not null,
	FOREIGN KEY (pizza_order_id) REFERENCES Pizza_Order(id),
	FOREIGN KEY (topping_id) REFERENCES Topping(id)
);

create table BreadStick_Order(
    id int not null auto_increment primary key,
	breadstick_id int not null,
	order_id int not null,
	quantity int not null,
	FOREIGN KEY (breadstick_id) REFERENCES BreadStick(id),
	FOREIGN KEY (order_id) REFERENCES UserOrder(id)
);

create table Drink_Order(
    id int not null auto_increment primary key,
	pizza_id int not null,
	drink_id int not null,
	quantity int not null,
	FOREIGN KEY (drink_id) REFERENCES Drink(id),
	FOREIGN KEY (order_id) REFERENCES UserOrder(id)
);


-- insert data into database

--four sizes of pizza: small, medium, large, x-large
insert into FoodBaseData values (1,723,6.15);
insert into Pizza values (1,1,1);
insert into FoodBaseData values (2,896,8.15);
insert into Pizza values (2,2,2);
insert into FoodBaseData values (3,1128,10.15);
insert into Pizza values (3,3,3);
insert into FoodBaseData values (4,1459,12.15);
insert into Pizza values (4,4,4);

insert into FoodBaseData values (5,89,0.30);
insert into Topping values (5,5,'Pepperoni');
insert into FoodBaseData values (6,34,0.20);
insert into Topping values (6,6,'Mushroom');
insert into FoodBaseData values (7,45,0.20);
insert into Topping values (7,7,'Olive');
insert into FoodBaseData values (8,132,0.35);
insert into Topping values (8,8,'Bacon');
insert into FoodBaseData values (9,105,0.30);
insert into Topping values (9,9,'Sausage');

insert into FoodBaseData values (10,110,1.35);
insert into FoodBaseData values (11,150,1.70);
insert into FoodBaseData values (12,220,2.15);
insert into Drink values (10,10,'S Coke');
insert into Drink values (10,10,'S Mountain Dew');
insert into Drink values (10,10,'S Crush');
insert into Drink values (11,11,'M Coke');
insert into Drink values (11,11,'M Mountain Dew');
insert into Drink values (11,11,'M Crush');
insert into Drink values (12,12,'L Coke');
insert into Drink values (12,12,'L Mountain Dew');
insert into Drink values (12,12,'L Crush');

insert into FoodBaseData values (13,660,5.35);
insert into FoodBaseData values (14,780,6.70);
insert into FoodBaseData values (15,750,6.90);
insert into BreadStick values (13,13,'Original');
insert into BreadStick values (14,14,'Cheesy Sticks');
insert into BreadStick values (15,14,'Cheesy Garlic Sticks');
