--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3
-- Dumped by pg_dump version 12.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: combinations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.combinations (
    combid integer NOT NULL,
    year1 integer,
    year2 integer,
    sourcetype text,
    location text
);


ALTER TABLE public.combinations OWNER TO postgres;

--
-- Name: combinations_combid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.combinations_combid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.combinations_combid_seq OWNER TO postgres;

--
-- Name: combinations_combid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.combinations_combid_seq OWNED BY public.combinations.combid;


--
-- Name: responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.responses (
    responseid integer NOT NULL,
    userid bigint NOT NULL,
    region text,
    year1 integer,
    year2 integer,
    answer integer
);


ALTER TABLE public.responses OWNER TO postgres;

--
-- Name: responses_responseid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.responses_responseid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.responses_responseid_seq OWNER TO postgres;

--
-- Name: responses_responseid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.responses_responseid_seq OWNED BY public.responses.responseid;


--
-- Name: satdata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.satdata (
    dataid integer NOT NULL,
    year integer,
    value integer,
    unit text,
    region text,
    country text,
    source text,
    sourcename text,
    sourcetype text
);


ALTER TABLE public.satdata OWNER TO postgres;

--
-- Name: satdata_dataid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.satdata_dataid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.satdata_dataid_seq OWNER TO postgres;

--
-- Name: satdata_dataid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.satdata_dataid_seq OWNED BY public.satdata.dataid;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    userid bigint NOT NULL,
    name text,
    location text,
    language text,
    referral_code text,
    last_played date,
    score integer
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: combinations combid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.combinations ALTER COLUMN combid SET DEFAULT nextval('public.combinations_combid_seq'::regclass);


--
-- Name: responses responseid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses ALTER COLUMN responseid SET DEFAULT nextval('public.responses_responseid_seq'::regclass);


--
-- Name: satdata dataid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.satdata ALTER COLUMN dataid SET DEFAULT nextval('public.satdata_dataid_seq'::regclass);


--
-- Data for Name: combinations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.combinations (combid, year1, year2, sourcetype, location) FROM stdin;
\.


--
-- Data for Name: responses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.responses (responseid, userid, region, year1, year2, answer) FROM stdin;
1	16468756700	New York	2017	2015	2017
2	16468756700	New York	2011	2004	2004
3	16468756700	New York	2009	2008	2009
\.


--
-- Data for Name: satdata; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.satdata (dataid, year, value, unit, region, country, source, sourcename, sourcetype) FROM stdin;
1	2000	15	mm	New York	USA	CHIRPS	PH	Rainfall
2	2001	15	mm	New York	USA	CHIRPS	PH	Rainfall
3	2002	10	mm	New York	USA	CHIRPS	PH	Rainfall
4	2003	12	mm	New York	USA	CHIRPS	PH	Rainfall
5	2004	6	mm	New York	USA	CHIRPS	PH	Rainfall
6	2005	13	mm	New York	USA	CHIRPS	PH	Rainfall
7	2006	12	mm	New York	USA	CHIRPS	PH	Rainfall
8	2007	18	mm	New York	USA	CHIRPS	PH	Rainfall
9	2008	4	mm	New York	USA	CHIRPS	PH	Rainfall
10	2009	7	mm	New York	USA	CHIRPS	PH	Rainfall
11	2010	8	mm	New York	USA	CHIRPS	PH	Rainfall
12	2011	9	mm	New York	USA	CHIRPS	PH	Rainfall
13	2012	6	mm	New York	USA	CHIRPS	PH	Rainfall
14	2013	13	mm	New York	USA	CHIRPS	PH	Rainfall
15	2014	1	mm	New York	USA	CHIRPS	PH	Rainfall
16	2015	2	mm	New York	USA	CHIRPS	PH	Rainfall
17	2016	19	mm	New York	USA	CHIRPS	PH	Rainfall
18	2017	18	mm	New York	USA	CHIRPS	PH	Rainfall
19	2018	10	mm	New York	USA	CHIRPS	PH	Rainfall
20	2019	15	mm	New York	USA	CHIRPS	PH	Rainfall
21	2000	12	mm	Boston	USA	CHIRPS	PH	Rainfall
22	2001	3	mm	Boston	USA	CHIRPS	PH	Rainfall
23	2002	4	mm	Boston	USA	CHIRPS	PH	Rainfall
24	2003	5	mm	Boston	USA	CHIRPS	PH	Rainfall
25	2004	13	mm	Boston	USA	CHIRPS	PH	Rainfall
26	2005	13	mm	Boston	USA	CHIRPS	PH	Rainfall
27	2006	15	mm	Boston	USA	CHIRPS	PH	Rainfall
28	2007	11	mm	Boston	USA	CHIRPS	PH	Rainfall
29	2008	19	mm	Boston	USA	CHIRPS	PH	Rainfall
30	2009	12	mm	Boston	USA	CHIRPS	PH	Rainfall
31	2010	10	mm	Boston	USA	CHIRPS	PH	Rainfall
32	2011	4	mm	Boston	USA	CHIRPS	PH	Rainfall
33	2012	7	mm	Boston	USA	CHIRPS	PH	Rainfall
34	2013	9	mm	Boston	USA	CHIRPS	PH	Rainfall
35	2014	6	mm	Boston	USA	CHIRPS	PH	Rainfall
36	2015	13	mm	Boston	USA	CHIRPS	PH	Rainfall
37	2016	19	mm	Boston	USA	CHIRPS	PH	Rainfall
38	2017	1	mm	Boston	USA	CHIRPS	PH	Rainfall
39	2018	4	mm	Boston	USA	CHIRPS	PH	Rainfall
40	2019	16	mm	Boston	USA	CHIRPS	PH	Rainfall
41	2000	11	mm	Taiwan	USA	CHIRPS	PH	Rainfall
42	2001	4	mm	Taiwan	USA	CHIRPS	PH	Rainfall
43	2002	9	mm	Taiwan	USA	CHIRPS	PH	Rainfall
44	2003	7	mm	Taiwan	USA	CHIRPS	PH	Rainfall
45	2004	16	mm	Taiwan	USA	CHIRPS	PH	Rainfall
46	2005	5	mm	Taiwan	USA	CHIRPS	PH	Rainfall
47	2006	4	mm	Taiwan	USA	CHIRPS	PH	Rainfall
48	2007	7	mm	Taiwan	USA	CHIRPS	PH	Rainfall
49	2008	9	mm	Taiwan	USA	CHIRPS	PH	Rainfall
50	2009	10	mm	Taiwan	USA	CHIRPS	PH	Rainfall
51	2010	18	mm	Taiwan	USA	CHIRPS	PH	Rainfall
52	2011	15	mm	Taiwan	USA	CHIRPS	PH	Rainfall
53	2012	17	mm	Taiwan	USA	CHIRPS	PH	Rainfall
54	2013	13	mm	Taiwan	USA	CHIRPS	PH	Rainfall
55	2014	4	mm	Taiwan	USA	CHIRPS	PH	Rainfall
56	2015	7	mm	Taiwan	USA	CHIRPS	PH	Rainfall
57	2016	8	mm	Taiwan	USA	CHIRPS	PH	Rainfall
58	2017	13	mm	Taiwan	USA	CHIRPS	PH	Rainfall
59	2018	11	mm	Taiwan	USA	CHIRPS	PH	Rainfall
60	2019	12	mm	Taiwan	USA	CHIRPS	PH	Rainfall
61	2000	48	degrees F	New York	USA	Laguardia	PH	Weather Station
62	2001	53	degrees F	New York	USA	Laguardia	PH	Weather Station
63	2002	21	degrees F	New York	USA	Laguardia	PH	Weather Station
64	2003	34	degrees F	New York	USA	Laguardia	PH	Weather Station
65	2004	56	degrees F	New York	USA	Laguardia	PH	Weather Station
66	2005	78	degrees F	New York	USA	Laguardia	PH	Weather Station
67	2006	12	degrees F	New York	USA	Laguardia	PH	Weather Station
68	2007	54	degrees F	New York	USA	Laguardia	PH	Weather Station
69	2008	68	degrees F	New York	USA	Laguardia	PH	Weather Station
70	2009	98	degrees F	New York	USA	Laguardia	PH	Weather Station
71	2010	8	degrees F	New York	USA	Laguardia	PH	Weather Station
72	2011	32	degrees F	New York	USA	Laguardia	PH	Weather Station
73	2012	43	degrees F	New York	USA	Laguardia	PH	Weather Station
74	2013	45	degrees F	New York	USA	Laguardia	PH	Weather Station
75	2014	45	degrees F	New York	USA	Laguardia	PH	Weather Station
76	2015	13	degrees F	New York	USA	Laguardia	PH	Weather Station
77	2016	13	degrees F	New York	USA	Laguardia	PH	Weather Station
78	2017	23	degrees F	New York	USA	Laguardia	PH	Weather Station
79	2018	22	degrees F	New York	USA	Laguardia	PH	Weather Station
80	2019	24	degrees F	New York	USA	Laguardia	PH	Weather Station
81	2000	34	degrees F	Boston	USA	Logan	PH	Weather Station
82	2001	34	degrees F	Boston	USA	Logan	PH	Weather Station
83	2002	45	degrees F	Boston	USA	Logan	PH	Weather Station
84	2003	67	degrees F	Boston	USA	Logan	PH	Weather Station
85	2004	87	degrees F	Boston	USA	Logan	PH	Weather Station
86	2005	43	degrees F	Boston	USA	Logan	PH	Weather Station
87	2006	13	degrees F	Boston	USA	Logan	PH	Weather Station
88	2007	24	degrees F	Boston	USA	Logan	PH	Weather Station
89	2008	55	degrees F	Boston	USA	Logan	PH	Weather Station
90	2009	45	degrees F	Boston	USA	Logan	PH	Weather Station
91	2010	55	degrees F	Boston	USA	Logan	PH	Weather Station
92	2011	65	degrees F	Boston	USA	Logan	PH	Weather Station
93	2012	78	degrees F	Boston	USA	Logan	PH	Weather Station
94	2013	65	degrees F	Boston	USA	Logan	PH	Weather Station
95	2014	32	degrees F	Boston	USA	Logan	PH	Weather Station
96	2015	32	degrees F	Boston	USA	Logan	PH	Weather Station
97	2016	44	degrees F	Boston	USA	Logan	PH	Weather Station
98	2017	55	degrees F	Boston	USA	Logan	PH	Weather Station
99	2018	88	degrees F	Boston	USA	Logan	PH	Weather Station
100	2019	12	degrees F	Boston	USA	Logan	PH	Weather Station
101	2000	54	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
102	2001	6	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
103	2002	54	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
104	2003	87	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
105	2004	98	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
106	2005	90	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
107	2006	76	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
108	2007	42	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
109	2008	32	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
110	2009	54	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
111	2010	65	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
112	2011	7	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
113	2012	65	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
114	2013	78	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
115	2014	89	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
116	2015	4	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
117	2016	3	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
118	2017	32	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
119	2018	44	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
120	2019	32	degrees F	Taiwan	USA	Taoyuan	PH	Weather Station
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (userid, name, location, language, referral_code, last_played, score) FROM stdin;
16468756700	Placeholder	New York	English	Placeholder	2020-07-02	250
\.


--
-- Name: combinations_combid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.combinations_combid_seq', 1, false);


--
-- Name: responses_responseid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.responses_responseid_seq', 3, true);


--
-- Name: satdata_dataid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.satdata_dataid_seq', 120, true);


--
-- Name: combinations combinations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.combinations
    ADD CONSTRAINT combinations_pkey PRIMARY KEY (combid);


--
-- Name: responses responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_pkey PRIMARY KEY (responseid);


--
-- Name: satdata satdata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.satdata
    ADD CONSTRAINT satdata_pkey PRIMARY KEY (dataid);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);


--
-- PostgreSQL database dump complete
--

