--
-- PostgreSQL database dump
--

\restrict 6oRw6b38dx0ytsmDHMRKoLQ7j9FpTIidW4CbcqohVQL3KFXh2CT32ezRAMxepet

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Tasks" (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    day_for date NOT NULL,
    is_finished boolean NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public."Tasks" OWNER TO postgres;

--
-- Name: Tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Tasks_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Tasks_id_seq" OWNER TO postgres;

--
-- Name: Tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Tasks_id_seq" OWNED BY public."Tasks".id;


--
-- Name: Users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Users" (
    id integer NOT NULL,
    username character varying(20) NOT NULL,
    email character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    profile_picture character varying(255)
);


ALTER TABLE public."Users" OWNER TO postgres;

--
-- Name: Users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Users_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Users_id_seq" OWNER TO postgres;

--
-- Name: Users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Users_id_seq" OWNED BY public."Users".id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: Tasks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tasks" ALTER COLUMN id SET DEFAULT nextval('public."Tasks_id_seq"'::regclass);


--
-- Name: Users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Users" ALTER COLUMN id SET DEFAULT nextval('public."Users_id_seq"'::regclass);


--
-- Data for Name: Tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Tasks" (id, name, day_for, is_finished, user_id) FROM stdin;
117	Тръгване за Слънчев бряг	2026-06-26	t	8
65	Математика - домашно - равноб. триъг. и трапец - sin и cos	2026-06-10	t	8
122	Тренировка	2026-07-06	f	8
68	домашно	2026-06-13	f	9
70	тренировка	2026-06-13	f	9
71	да се изкъпя	2026-06-14	f	9
72	разходка	2026-06-14	t	9
69	да отида до магазина	2026-06-13	t	9
52	Физика - изходно ниво	2026-06-22	t	8
110	Програмиране практика - изпитване	2026-06-23	t	8
97	Електротехника - презентация	2026-06-19	t	8
10	sgfgf	2026-06-01	f	8
11	trwtre	2026-06-01	f	8
12	grgset	2026-06-01	f	8
13	gg	2026-06-02	t	8
14	a	2026-06-03	f	8
15	hfgdfvcd	2026-06-02	f	8
17	gdfsd	2026-06-02	f	8
16	gdfsd	2026-06-02	t	8
102	нокти	2026-06-19	t	8
59	Предприемачество презентация с много изисквания - Сашо и Матей	2026-06-16	t	8
44	презентация по физика - Сашо	2026-06-08	t	8
101	.bat файл за изтриване на Opera Setup	2026-06-19	t	8
93	Компютърни мрежи - домашно	2026-06-20	t	8
53	Програмиране - преговор за изпитване	2026-06-16	t	8
45	мат. - дом. - подготовка с Gemini и други домашни за колата	2026-06-08	t	8
46	тубата - песни - запазване	2026-06-08	t	8
123	Песни	2026-06-29	t	8
112	Философия - презентация за Поп изкуство	2026-06-22	t	8
22	rvefdw	2026-06-06	f	8
40	домашно по програмиране	2026-06-07	t	8
24	vdcsx	2026-06-06	t	8
106	Литература - зубрене за тест утре	2026-06-23	t	8
107	Математика тест - РП	2026-06-24	t	8
119	ТУЕС - обратна връзка	2026-06-29	t	8
94	Математика - подготовка за тест по РП	2026-06-21	t	8
95	Английски - тетрадка	2026-06-21	t	8
121	Взимане на учебниците	2026-06-30	t	8
127	Четка и паста за зъби	2026-06-30	t	8
115	Неща направени преди лятото	2026-07-01	f	8
120	Психолог	2026-06-30	t	8
96	Правене на презентацията по История с Косьо за Падането на Тодор Живков	2026-06-17	t	8
57	Литература - подготовка за тест и изпитване	2026-06-17	f	8
62	Компютърни мрежи - тест	2026-06-25	t	8
90	Математика - преговор за тест на неравенства	2026-06-15	t	8
91	Градивни елементи - 3 теста утре сутринта	2026-06-15	t	8
56	Математика - учене за неравенства	2026-06-14	t	8
63	Зубрене на презентацията по История	2026-06-18	t	8
118	Европейска купа по трудност в Австрия, Дорнбирн	2026-07-03	f	8
116	Изпитване по български	2026-06-26	t	8
100	Туба за вода	2026-06-18	t	8
128	План за лятото	2026-07-02	f	8
126	Поръчване от Тему	2026-06-30	t	8
125	handstand	2026-06-30	t	8
111	Публикуване на сайта	2026-06-30	t	8
129	Пак да пробвам да публикувам сайта	2026-07-01	f	8
\.


--
-- Data for Name: Users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Users" (id, username, email, password, profile_picture) FROM stdin;
8	Georgi Merdjanov	georgi.merdjanov10@gmail.com	scrypt:32768:8:1$AH068CQq3tZWQZHo$bac0b4232f3f64cb65a825269e9f061a8a0772ffe1d4f0cb8ed71910e2614af35e84139910a4de6e52b7cab920020deb74cfa13b5188d3b3ef7f759562d27075	8.png
9	admin	admin@gmail.com	scrypt:32768:8:1$WVXBdY8l2MK2VvM9$4fc284e323ecb793c9931e83e772f1f6ab7f443708d8a01b37dd7ce1c6580c8e456163d01abf1b425fee4627358473d278bbbe41208ca5c935c9875e6699b8ce	9.png
10	Гого Атанасов	katerach18g@gmail.com	scrypt:32768:8:1$27rDbkMCCwDlmWsh$cb0a4a2fb658b378024a36eb12bff540f76c2a1e5f3ea4fedb2946ca6faf8459b644a1f967519748040a648719dcd5fb4c56e1a2d3da91a9fa98a8f534e555c3	\N
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
a50bcd3d4cf3
\.


--
-- Name: Tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."Tasks_id_seq"', 129, true);


--
-- Name: Users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."Users_id_seq"', 13, true);


--
-- Name: Tasks Tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tasks"
    ADD CONSTRAINT "Tasks_pkey" PRIMARY KEY (id);


--
-- Name: Users Users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_email_key" UNIQUE (email);


--
-- Name: Users Users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_pkey" PRIMARY KEY (id);


--
-- Name: Users Users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_username_key" UNIQUE (username);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: Tasks fk_task_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Tasks"
    ADD CONSTRAINT fk_task_user FOREIGN KEY (user_id) REFERENCES public."Users"(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 6oRw6b38dx0ytsmDHMRKoLQ7j9FpTIidW4CbcqohVQL3KFXh2CT32ezRAMxepet

