-- Запросы для анализа данных автосалона.
-- Их можно запускать напрямую в SQLite или через main.py.

-- 1. Покупатели, которым подходит грузовой автомобиль до 2 млн и не старше 2020 г.
SELECT DISTINCT
    p.ID_покупателя AS id_покупателя,
    p.ФИО AS покупатель,
    p.бюджет,
    a.ID_авто AS id_авто,
    a.марка,
    a.год_выпуска,
    a.стоимость,
    p.бюджет - a.стоимость AS остаток_бюджета
FROM Покупатель AS p
JOIN Авто AS a
    ON p.бюджет >= a.стоимость
JOIN Марки AS m
    ON a.марка = m.марка
WHERE m.категория = 'грузовая'
    AND a.год_выпуска >= 2020
    AND a.стоимость <= 2000000
ORDER BY p.бюджет DESC, a.стоимость DESC;

-- 2. Сколько продаж было покупателям, чей год рождения совпадает с годом выпуска авто.
SELECT
    COUNT(*) AS количество_продаж,
    COUNT(DISTINCT p.ID_покупателя) AS количество_покупателей
FROM Покупатель AS p
JOIN Продажи AS s
    ON p.ID_покупателя = s.ID_покупателя
JOIN Авто AS a
    ON s.ID_авто = a.ID_авто
WHERE strftime('%Y', p.дата_рождения) = CAST(a.год_выпуска AS TEXT);

-- 3. Продажи администраторов покупателям без водительских прав.
SELECT
    seller.ID_продавца AS id_продавца,
    seller.ФИО AS продавец,
    COUNT(*) AS количество_продаж,
    SUM(s.стоимость) AS выручка
FROM Продажи AS s
JOIN Продавец AS seller
    ON s.ID_продавца = seller.ID_продавца
JOIN Покупатель AS p
    ON s.ID_покупателя = p.ID_покупателя
WHERE seller.должность = 'администратор'
    AND p.наличие_прав = 'нету'
GROUP BY seller.ID_продавца, seller.ФИО
ORDER BY количество_продаж DESC, выручка DESC;

-- 4. Выручка и количество продаж по маркам автомобилей.
SELECT
    m.категория,
    a.марка,
    COUNT(*) AS количество_продаж,
    SUM(s.стоимость) AS выручка,
    ROUND(AVG(s.стоимость), 2) AS средняя_цена_продажи
FROM Продажи AS s
JOIN Авто AS a
    ON s.ID_авто = a.ID_авто
JOIN Марки AS m
    ON a.марка = m.марка
GROUP BY m.категория, a.марка
ORDER BY выручка DESC;

-- 5. Рейтинг продавцов по количеству продаж и выручке.
SELECT
    seller.ID_продавца AS id_продавца,
    seller.ФИО AS продавец,
    seller.должность,
    COUNT(*) AS количество_продаж,
    SUM(s.стоимость) AS выручка
FROM Продажи AS s
JOIN Продавец AS seller
    ON s.ID_продавца = seller.ID_продавца
GROUP BY seller.ID_продавца, seller.ФИО, seller.должность
ORDER BY выручка DESC, количество_продаж DESC;

-- 6. Базовые проверки качества данных: нет ли продаж без связанных записей.
SELECT
    SUM(CASE WHEN a.ID_авто IS NULL THEN 1 ELSE 0 END) AS продажи_без_авто,
    SUM(CASE WHEN seller.ID_продавца IS NULL THEN 1 ELSE 0 END) AS продажи_без_продавца,
    SUM(CASE WHEN p.ID_покупателя IS NULL THEN 1 ELSE 0 END) AS продажи_без_покупателя
FROM Продажи AS s
LEFT JOIN Авто AS a
    ON s.ID_авто = a.ID_авто
LEFT JOIN Продавец AS seller
    ON s.ID_продавца = seller.ID_продавца
LEFT JOIN Покупатель AS p
    ON s.ID_покупателя = p.ID_покупателя;
