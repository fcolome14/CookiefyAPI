﻿-- ===============================
-- IMPORTANT NOTE: These files must be saved as UTF-8 without BOM.
-- To do so, in Visual Studio Code, go to VSC right bottom (UTF-8) and click it > Save with Encoding > UTF-8.
-- ===============================

TRUNCATE TABLE hashtags RESTART IDENTITY CASCADE;
TRUNCATE TABLE categories RESTART IDENTITY CASCADE;
TRUNCATE TABLE images RESTART IDENTITY CASCADE;
TRUNCATE TABLE images RESTART IDENTITY CASCADE;
TRUNCATE TABLE users RESTART IDENTITY CASCADE;

-- ===============================
-- System Users
-- ===============================
-- sys_01 --> sys_ck
INSERT INTO users (id, name, email, username, hashed_password, is_active) VALUES
(1, 'Admin', 'cookiefy@gmail.com', 'sys_01', '$2b$12$FKalRH4tKSi6SuIjacsTz.1ISWc3Baws0Ptbi1iZ1BWj8DynLbN7e', true)
ON CONFLICT (id) DO NOTHING;

-- ===============================
-- Static Images
-- ===============================
INSERT INTO images (id, name, path) VALUES
(1, 'default-no_image.png', 'defaults/default-no_image.png'),
(2, 'default-no_image_2.png', 'defaults/default-no_image_2.png'),
(3, 'drink-beer.png', 'defaults/drink-beer.png'),
(4, 'drink-cocktail.png', 'defaults/drink-cocktail.png'),
(5, 'drink-wine.png', 'defaults/drink-wine.png'),
(6, 'food-argentinian.png', 'defaults/food-argentinian.png'),
(7, 'food-asian.png', 'defaults/food-asian.png'),
(8, 'food-bakery.png', 'defaults/food-bakery.png'),
(9, 'food-balearic.png', 'defaults/food-balearic.png'),
(10, 'food-bbq.png', 'defaults/food-bbq.png'),
(11, 'food-brazilian.png', 'defaults/food-brazilian.png'),
(12, 'food-brit.png', 'defaults/food-brit.png'),
(13, 'food-calsot.png', 'defaults/food-calsot.png'),
(14, 'food-caribbean.png', 'defaults/food-caribbean.png'),
(15, 'food-catalan.png', 'defaults/food-catalan.png'),
(16, 'food-cheese.png', 'defaults/food-cheese.png'),
(17, 'food-chinese.png', 'defaults/food-chinese.png'),
(18, 'food-croquetas.png', 'defaults/food-croquetas.png'),
(19, 'food-dessert.png', 'defaults/food-dessert.png'),
(20, 'food-european.png', 'defaults/food-european.png'),
(21, 'food-fast_food.png', 'defaults/food-fast_food.png'),
(22, 'food-fish.png', 'defaults/food-fish.png'),
(23, 'food-french.png', 'defaults/food-french.png'),
(24, 'food-greek.png', 'defaults/food-greek.png'),
(25, 'food-ice_cream.png', 'defaults/food-ice_cream.png'),
(26, 'food-indian.png', 'defaults/food-indian.png'),
(27, 'food-italian.png', 'defaults/food-italian.png'),
(28, 'food-japanese.png', 'defaults/food-japanese.png'),
(29, 'food-kebab.png', 'defaults/food-kebab.png'),
(30, 'food-kenian.png', 'defaults/food-kenian.png'),
(31, 'food-korean.png', 'defaults/food-korean.png'),
(32, 'food-libanese.png', 'defaults/food-libanese.png'),
(33, 'food-meat.png', 'defaults/food-meat.png'),
(34, 'food-med.png', 'defaults/food-med.png'),
(35, 'food-mexican.png', 'defaults/food-mexican.png'),
(36, 'food-morrocco.png', 'defaults/food-morrocco.png'),
(37, 'food-omelette.png', 'defaults/food-omelette.png'),
(38, 'food-peruvian.png', 'defaults/food-peruvian.png'),
(39, 'food-pizza.png', 'defaults/food-pizza.png'),
(40, 'food-russian.png', 'defaults/food-russian.png'),
(41, 'food-spanish.png', 'defaults/food-spanish.png'),
(42, 'food-spicy.png', 'defaults/food-spicy.png'),
(43, 'food-sushi.png', 'defaults/food-sushi.png'),
(44, 'food-tacos.png', 'defaults/food-tacos.png'),
(45, 'food-tapas.png', 'defaults/food-tapas.png'),
(46, 'food-thai.png', 'defaults/food-thai.png'),
(47, 'food-turk.png', 'defaults/food-turk.png'),
(48, 'food-usa.png', 'defaults/food-usa.png'),
(49, 'food-vegetables.png', 'defaults/food-vegetables.png'),
(50, 'food-veggan.png', 'defaults/food-veggan.png'),
(51, 'food-viet.png', 'defaults/food-viet.png'),
(52, 'site-bar.png', 'defaults/site-bar.png'),
(53, 'site-cellar.png', 'defaults/site-cellar.png'),
(54, 'site-pub.png', 'defaults/site-pub.png'),
(55, 'food-basque.png', 'defaults/food-basque.png'),
(56, 'food-german.png', 'defaults/food-german.png'),
(57, 'food-venezuela.png', 'defaults/food-venezuela.png'),
(58, 'food-irish.png', 'defaults/food-irish.png'),
(59, 'food-oriental.png', 'defaults/food-oriental.png'),
(60, 'food-fusion.png', 'defaults/food-fusion.png'),
(61, 'food-arabic.png', 'defaults/food-arabic.png'),
(62, 'food-cuban.png', 'defaults/food-cuban.png'),
(63, 'food-aragon.png', 'defaults/food-aragon.png'),
(64, 'food-anadalusia.png', 'defaults/food-andalusia.png'),
(65, 'food-african.png', 'defaults/food-african.png'),
(66, 'chart-top-50-global-lists.png', 'defaults/chart-top-50-global-lists.png'),
(67, 'chart-top-50-global-restaurants.png', 'defaults/chart-top-50-global-restaurants.png'),
(68, 'chart-top-50-nearby-restaurants.png', 'defaults/chart-top-50-nearby-restaurants.png')
ON CONFLICT (id) DO NOTHING;

-- ===============================
-- Static Categories
-- ===============================
INSERT INTO categories (id, name) VALUES
(1, 'Restaurant'),
(2, 'Bar'),
(3, 'Pub'),
(4, 'Café'),
(5, 'Street Food')
ON CONFLICT (id) DO NOTHING;

-- ===============================
-- Static Hashtags
-- ===============================
INSERT INTO hashtags (id, name, image_id) VALUES
(1, 'Asian', 7),
(2, 'Mexican', 35),
(3, 'Spanish', 41),
(4, 'Italian', 27),
(5, 'French', 23),
(6, 'American', 48),
(7, 'Indian', 26),
(8, 'Mediterranean', 34),
(9, 'Restaurant', NULL),
(10, 'Bar', 52),
(11, 'Cocktails', 4),
(12, 'Japanese', 28),
(13, 'Chinese', 17),
(14, 'Catalan', 15),
(15, 'Thai', 46),
(16, 'Vietnamese', 51),
(17, 'Korean', 31),
(18, 'Turkish', 47),
(19, 'Greek', 24),
(20, 'Lebanese', 32),
(21, 'Moroccan', 36),
(22, 'Brazilian', 11),
(23, 'Peruvian', 38),
(24, 'Argentinian', 6),
(25, 'Caribbean', 14),
(26, 'African', NULL),
(27, 'Vegan', 50),
(28, 'Vegetarian', 49),
(29, 'Gluten-Free', NULL),
(30, 'Steakhouse', 33),
(31, 'Seafood', 22),
(32, 'Burger', NULL),
(33, 'Pizza', 39),
(34, 'Tapas', 45),
(35, 'Brunch', NULL),
(36, 'Coffee', NULL),
(37, 'Bakery', 8),
(38, 'Ice Cream', 25),
(39, 'Sushi', 43),
(40, 'Ramen', NULL),
(41, 'Fast Food', 21),
(42, 'Fine Dining', NULL),
(43, 'Casual Dining', NULL),
(44, 'Street Food', NULL),
(45, 'Fusion', 60),
(46, 'Buffet', NULL),
(47, 'Wine Bar', 5),
(48, 'Craft Beer', 3),
(49, 'Deli', NULL),
(50, 'Gastropub', NULL),
(51, 'Food Truck', NULL),
(52, 'Pasta', NULL),
(53, 'Salad', NULL),
(54, 'Dessert', 19),
(55, 'Brasserie', NULL),
(56, 'Bistro', NULL),
(57, 'Cafe', 4),
(58, 'Patisserie', NULL),
(59, 'Taverna', NULL),
(60, 'Trattoria', NULL),
(61, 'Taverne', NULL),
(62, 'Churrascaria', 11),
(63, 'Parrilla', 33),
(64, 'Asador', 33),
(65, 'Taqueria', 44),
(66, 'BBQ', 10),
(67, 'Andalusian', NULL),
(68, 'Arab', 61),
(69, 'Aragonese', NULL),
(70, 'Asturian', NULL),
(71, 'Balearic', 9),
(72, 'Basque', 55),
(73, 'Canarian', NULL),
(74, 'Castilian', NULL),
(75, 'Chilean', NULL),
(76, 'Colombian', NULL),
(77, 'Cuban', 62),
(78, 'Galician', NULL),
(79, 'Honduran', NULL),
(80, 'Nicaraguan', NULL),
(81, 'Panamanian', NULL),
(82, 'Paraguayan', NULL),
(83, 'Peruvian', 38),
(84, 'Puerto Rican', NULL),
(85, 'Salvadoran', NULL),
(86, 'Uruguayan', NULL),
(87, 'Venezuelan', 57),
(88, 'Ecuadorian', NULL),
(89, 'Extremadura', NULL),
(90, 'German', 56),
(91, 'Irish', 58),
(92, 'Leonese', NULL),
(93, 'Murcian', NULL),
(94, 'Riojan', NULL),
(95, 'Romanian', NULL),
(96, 'Creperie', NULL),
(97, 'Pinchos', NULL),
(98, 'Calsots', 13),
(99, 'Contemporary', NULL),
(100, 'International', NULL),
(101, 'Oriental', 59)
ON CONFLICT (id) DO NOTHING;

SELECT setval('images_id_seq', (SELECT MAX(id) FROM images));
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('hashtags_id_seq', (SELECT MAX(id) FROM hashtags));