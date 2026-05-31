-- Структура базы данных автосалона.

-- Таблица: Авто
CREATE TABLE Авто (
    ID_авто INTEGER PRIMARY KEY AUTOINCREMENT,
    марка TEXT NOT NULL,
    год_выпуска INTEGER NOT NULL,
    стоимость INTEGER NOT NULL,
    FOREIGN KEY (марка) REFERENCES Марки(марка)
);

-- Таблица: Марки
CREATE TABLE Марки (
    марка TEXT PRIMARY KEY,
    категория TEXT NOT NULL
);

-- Таблица: Покупатель
CREATE TABLE Покупатель (
    ID_покупателя INTEGER PRIMARY KEY AUTOINCREMENT,
    ФИО TEXT NOT NULL,
    наличие_прав TEXT NOT NULL CHECK (наличие_прав IN ('есть', 'нету')),
    бюджет INTEGER NOT NULL,
    дата_рождения DATE NOT NULL
);

-- Таблица: Продавец
CREATE TABLE Продавец (
    ID_продавца INTEGER PRIMARY KEY AUTOINCREMENT,
    ФИО TEXT NOT NULL,
    должность TEXT NOT NULL
);

-- Таблица: Продажи
CREATE TABLE Продажи (
    ID_продажи INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_авто INTEGER NOT NULL,
    ID_продавца INTEGER NOT NULL,
    ID_покупателя INTEGER NOT NULL,
    стоимость INTEGER NOT NULL,
    FOREIGN KEY (ID_авто) REFERENCES Авто(ID_авто),
    FOREIGN KEY (ID_продавца) REFERENCES Продавец(ID_продавца),
    FOREIGN KEY (ID_покупателя) REFERENCES Покупатель(ID_покупателя)
);

