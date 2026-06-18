--
-- PostgreSQL database dump
--

\restrict C4340EfjMvb4JP3RrKfDv5uPLocctVrP8JuRKLMfOlBr1BEzLy2QtU47DXW2sO9

-- Dumped from database version 17.7 (Debian 17.7-3.pgdg13+1)
-- Dumped by pg_dump version 17.10 (Homebrew)

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
-- Name: action_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.action_plans (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    last_trade_id bigint NOT NULL,
    buy_title character varying(200) NOT NULL,
    buy_summary text NOT NULL,
    buy_referenced_trade_ids jsonb NOT NULL,
    sell_title character varying(200) NOT NULL,
    sell_summary text NOT NULL,
    sell_referenced_trade_ids jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    buy_rule text,
    sell_rule text
);


ALTER TABLE public.action_plans OWNER TO postgres;

--
-- Name: action_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.action_plans_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.action_plans_id_seq OWNER TO postgres;

--
-- Name: action_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.action_plans_id_seq OWNED BY public.action_plans.id;


--
-- Name: asset_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asset_prices (
    ticker character varying(16) NOT NULL,
    price numeric(18,6) NOT NULL,
    change numeric(18,6),
    change_rate numeric(18,8),
    captured_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.asset_prices OWNER TO postgres;

--
-- Name: assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assets (
    ticker character varying(16) NOT NULL,
    name character varying(255) NOT NULL,
    currency character varying(8),
    market_cap numeric(20,2),
    meta_updated_at timestamp with time zone DEFAULT now() NOT NULL,
    sector character varying(100)
);


ALTER TABLE public.assets OWNER TO postgres;

--
-- Name: holdings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.holdings (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    ticker character varying(16) NOT NULL,
    quantity integer NOT NULL,
    average_price numeric(18,4),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_holdings_avg_price CHECK (((average_price IS NULL) OR (average_price >= (0)::numeric))),
    CONSTRAINT chk_holdings_quantity CHECK ((quantity >= 0))
);


ALTER TABLE public.holdings OWNER TO postgres;

--
-- Name: holdings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.holdings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.holdings_id_seq OWNER TO postgres;

--
-- Name: holdings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.holdings_id_seq OWNED BY public.holdings.id;


--
-- Name: portfolio_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.portfolio_snapshots (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    captured_date date NOT NULL,
    total_value numeric(18,4) NOT NULL,
    total_profit_rate numeric(10,6),
    total_profit_amount numeric(18,4),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_total_value CHECK ((total_value >= (0)::numeric))
);


ALTER TABLE public.portfolio_snapshots OWNER TO postgres;

--
-- Name: portfolio_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.portfolio_snapshots_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.portfolio_snapshots_id_seq OWNER TO postgres;

--
-- Name: portfolio_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.portfolio_snapshots_id_seq OWNED BY public.portfolio_snapshots.id;


--
-- Name: sector_summaries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sector_summaries (
    id bigint NOT NULL,
    sector_id bigint NOT NULL,
    title character varying(200) NOT NULL,
    summary_date date NOT NULL,
    preview character varying(400) NOT NULL,
    content text NOT NULL,
    key_points jsonb NOT NULL,
    sources jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sector_summaries OWNER TO postgres;

--
-- Name: sector_summaries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sector_summaries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sector_summaries_id_seq OWNER TO postgres;

--
-- Name: sector_summaries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sector_summaries_id_seq OWNED BY public.sector_summaries.id;


--
-- Name: sectors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sectors (
    id bigint NOT NULL,
    sector_key character varying(50) NOT NULL,
    sector_display character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sectors OWNER TO postgres;

--
-- Name: sectors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sectors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sectors_id_seq OWNER TO postgres;

--
-- Name: sectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sectors_id_seq OWNED BY public.sectors.id;


--
-- Name: ticker_news; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticker_news (
    id bigint NOT NULL,
    ticker_id bigint NOT NULL,
    article_id character varying(200) NOT NULL,
    title text NOT NULL,
    summary text,
    source character varying(100),
    url text,
    published_at timestamp without time zone,
    snapshot_date date NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ticker_news OWNER TO postgres;

--
-- Name: ticker_news_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ticker_news_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ticker_news_id_seq OWNER TO postgres;

--
-- Name: ticker_news_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ticker_news_id_seq OWNED BY public.ticker_news.id;


--
-- Name: tickers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tickers (
    id bigint NOT NULL,
    sector_id bigint NOT NULL,
    ticker character varying(10) NOT NULL,
    company_name character varying(200) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.tickers OWNER TO postgres;

--
-- Name: tickers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tickers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tickers_id_seq OWNER TO postgres;

--
-- Name: tickers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tickers_id_seq OWNED BY public.tickers.id;


--
-- Name: trade_market_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trade_market_snapshots (
    id bigint NOT NULL,
    trade_id bigint NOT NULL,
    type character varying(10) NOT NULL,
    range character varying(10),
    captured_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_snapshot_type CHECK (((type)::text = ANY ((ARRAY['quant'::character varying, 'qual'::character varying])::text[])))
);


ALTER TABLE public.trade_market_snapshots OWNER TO postgres;

--
-- Name: trade_market_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trade_market_snapshots_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trade_market_snapshots_id_seq OWNER TO postgres;

--
-- Name: trade_market_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trade_market_snapshots_id_seq OWNED BY public.trade_market_snapshots.id;


--
-- Name: trade_positions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trade_positions (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    ticker character varying(16) NOT NULL,
    status character varying(10) DEFAULT 'OPEN'::character varying NOT NULL,
    opened_at timestamp with time zone DEFAULT now() NOT NULL,
    closed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_trade_positions_status CHECK (((status)::text = ANY ((ARRAY['OPEN'::character varying, 'CLOSED'::character varying])::text[])))
);


ALTER TABLE public.trade_positions OWNER TO postgres;

--
-- Name: trade_positions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trade_positions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trade_positions_id_seq OWNER TO postgres;

--
-- Name: trade_positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trade_positions_id_seq OWNED BY public.trade_positions.id;


--
-- Name: trade_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trade_results (
    trade_id bigint NOT NULL,
    pnl_status character varying(10) DEFAULT 'OPEN'::character varying NOT NULL,
    pnl_amount numeric(18,4),
    pnl_rate numeric(10,6),
    closed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_pnl_status CHECK (((pnl_status)::text = ANY ((ARRAY['OPEN'::character varying, 'CLOSED'::character varying])::text[])))
);


ALTER TABLE public.trade_results OWNER TO postgres;

--
-- Name: trades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trades (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    ticker character varying(16) NOT NULL,
    trade_type character varying(10) NOT NULL,
    trade_date date NOT NULL,
    price numeric(18,4) NOT NULL,
    quantity integer NOT NULL,
    confidence integer,
    behavior_type character varying(50) NOT NULL,
    memo character varying(2000),
    position_action character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    position_id bigint,
    CONSTRAINT chk_trade_behavior_type CHECK (((behavior_type)::text = ANY ((ARRAY['MOMENTUM'::character varying, 'TREND_FOLLOW_UP'::character varying, 'DIP_BUY'::character varying, 'RECOVERY_HOPE'::character varying, 'NEWS_REACTION'::character varying, 'POLICY_EVENT_REACTION'::character varying, 'EARNINGS_PLAY'::character varying, 'FUNDAMENTAL_BELIEF'::character varying, 'REPORT_BASED'::character varying, 'SECTOR_ROTATION'::character varying, 'CHART_PATTERN'::character varying, 'INDICATOR_BASED'::character varying, 'SCOUTING'::character varying, 'SPLIT_BUY'::character varying, 'EXPERIMENTAL'::character varying, 'REBALANCING'::character varying, 'AVERAGING_DOWN'::character varying, 'HERD_FOLLOWING'::character varying, 'TARGET_HIT'::character varying, 'QUICK_PROFIT'::character varying, 'LOSS_LIMIT'::character varying, 'DOWNSIDE_DEFENSE'::character varying, 'TECH_SIGNAL'::character varying, 'FUNDAMENTAL_CHANGE'::character varying, 'VOLATILITY_RESPONSE'::character varying, 'PORTFOLIO_ADJUSTMENT'::character varying, 'BETTER_OPPORTUNITY'::character varying, 'EMERGENCY_LIQUIDITY'::character varying, 'PLANNED_LIQUIDATION'::character varying, 'FEAR_SELL'::character varying, 'SELF_BLAME_SELL'::character varying])::text[]))),
    CONSTRAINT chk_trade_confidence CHECK (((confidence IS NULL) OR ((confidence >= 0) AND (confidence <= 100)))),
    CONSTRAINT chk_trade_position_action CHECK (((position_action)::text = ANY ((ARRAY['ENTRY'::character varying, 'ADD'::character varying, 'PARTIAL_EXIT'::character varying, 'EXIT'::character varying])::text[]))),
    CONSTRAINT chk_trade_price CHECK ((price > (0)::numeric)),
    CONSTRAINT chk_trade_quantity CHECK ((quantity > 0)),
    CONSTRAINT chk_trade_type CHECK (((trade_type)::text = ANY ((ARRAY['BUY'::character varying, 'SELL'::character varying])::text[])))
);


ALTER TABLE public.trades OWNER TO postgres;

--
-- Name: trades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trades_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trades_id_seq OWNER TO postgres;

--
-- Name: trades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trades_id_seq OWNED BY public.trades.id;


--
-- Name: user_interest_sectors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_interest_sectors (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    sector_id bigint NOT NULL,
    registered_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_interest_sectors OWNER TO postgres;

--
-- Name: user_interest_sectors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_interest_sectors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_interest_sectors_id_seq OWNER TO postgres;

--
-- Name: user_interest_sectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_interest_sectors_id_seq OWNED BY public.user_interest_sectors.id;


--
-- Name: user_refresh_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_refresh_tokens (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    refresh_token character varying(500) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    revoked_at timestamp without time zone
);


ALTER TABLE public.user_refresh_tokens OWNER TO postgres;

--
-- Name: user_refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_refresh_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_refresh_tokens_id_seq OWNER TO postgres;

--
-- Name: user_refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_refresh_tokens_id_seq OWNED BY public.user_refresh_tokens.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    email character varying(50),
    provider character varying(50) NOT NULL,
    provider_id character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    nickname character varying(100),
    profile_image character varying(500)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: watchlist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.watchlist (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    ticker character varying(16) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.watchlist OWNER TO postgres;

--
-- Name: watchlist_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.watchlist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.watchlist_id_seq OWNER TO postgres;

--
-- Name: watchlist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.watchlist_id_seq OWNED BY public.watchlist.id;


--
-- Name: action_plans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.action_plans ALTER COLUMN id SET DEFAULT nextval('public.action_plans_id_seq'::regclass);


--
-- Name: holdings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holdings ALTER COLUMN id SET DEFAULT nextval('public.holdings_id_seq'::regclass);


--
-- Name: portfolio_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_snapshots ALTER COLUMN id SET DEFAULT nextval('public.portfolio_snapshots_id_seq'::regclass);


--
-- Name: sector_summaries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sector_summaries ALTER COLUMN id SET DEFAULT nextval('public.sector_summaries_id_seq'::regclass);


--
-- Name: sectors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sectors ALTER COLUMN id SET DEFAULT nextval('public.sectors_id_seq'::regclass);


--
-- Name: ticker_news id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticker_news ALTER COLUMN id SET DEFAULT nextval('public.ticker_news_id_seq'::regclass);


--
-- Name: tickers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickers ALTER COLUMN id SET DEFAULT nextval('public.tickers_id_seq'::regclass);


--
-- Name: trade_market_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_market_snapshots ALTER COLUMN id SET DEFAULT nextval('public.trade_market_snapshots_id_seq'::regclass);


--
-- Name: trade_positions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_positions ALTER COLUMN id SET DEFAULT nextval('public.trade_positions_id_seq'::regclass);


--
-- Name: trades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades ALTER COLUMN id SET DEFAULT nextval('public.trades_id_seq'::regclass);


--
-- Name: user_interest_sectors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_interest_sectors ALTER COLUMN id SET DEFAULT nextval('public.user_interest_sectors_id_seq'::regclass);


--
-- Name: user_refresh_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.user_refresh_tokens_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: watchlist id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watchlist ALTER COLUMN id SET DEFAULT nextval('public.watchlist_id_seq'::regclass);


--
-- Name: action_plans action_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.action_plans
    ADD CONSTRAINT action_plans_pkey PRIMARY KEY (id);


--
-- Name: asset_prices asset_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_prices
    ADD CONSTRAINT asset_prices_pkey PRIMARY KEY (ticker);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (ticker);


--
-- Name: holdings holdings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holdings
    ADD CONSTRAINT holdings_pkey PRIMARY KEY (id);


--
-- Name: portfolio_snapshots portfolio_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_snapshots
    ADD CONSTRAINT portfolio_snapshots_pkey PRIMARY KEY (id);


--
-- Name: sector_summaries sector_summaries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sector_summaries
    ADD CONSTRAINT sector_summaries_pkey PRIMARY KEY (id);


--
-- Name: sectors sectors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sectors
    ADD CONSTRAINT sectors_pkey PRIMARY KEY (id);


--
-- Name: sectors sectors_sector_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sectors
    ADD CONSTRAINT sectors_sector_key_key UNIQUE (sector_key);


--
-- Name: ticker_news ticker_news_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticker_news
    ADD CONSTRAINT ticker_news_pkey PRIMARY KEY (id);


--
-- Name: ticker_news ticker_news_ticker_id_article_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticker_news
    ADD CONSTRAINT ticker_news_ticker_id_article_id_key UNIQUE (ticker_id, article_id);


--
-- Name: tickers tickers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickers
    ADD CONSTRAINT tickers_pkey PRIMARY KEY (id);


--
-- Name: tickers tickers_sector_id_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickers
    ADD CONSTRAINT tickers_sector_id_ticker_key UNIQUE (sector_id, ticker);


--
-- Name: trade_market_snapshots trade_market_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_market_snapshots
    ADD CONSTRAINT trade_market_snapshots_pkey PRIMARY KEY (id);


--
-- Name: trade_positions trade_positions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_positions
    ADD CONSTRAINT trade_positions_pkey PRIMARY KEY (id);


--
-- Name: trade_results trade_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_results
    ADD CONSTRAINT trade_results_pkey PRIMARY KEY (trade_id);


--
-- Name: trades trades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_pkey PRIMARY KEY (id);


--
-- Name: sector_summaries uk_sector_summary_daily; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sector_summaries
    ADD CONSTRAINT uk_sector_summary_daily UNIQUE (sector_id, summary_date);


--
-- Name: user_interest_sectors uk_user_sector; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_interest_sectors
    ADD CONSTRAINT uk_user_sector UNIQUE (user_id, sector_id);


--
-- Name: holdings uq_holdings_user_ticker; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holdings
    ADD CONSTRAINT uq_holdings_user_ticker UNIQUE (user_id, ticker);


--
-- Name: portfolio_snapshots uq_portfolio_user_date; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_snapshots
    ADD CONSTRAINT uq_portfolio_user_date UNIQUE (user_id, captured_date);


--
-- Name: trade_market_snapshots uq_trade_snapshot; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_market_snapshots
    ADD CONSTRAINT uq_trade_snapshot UNIQUE (trade_id, type, range);


--
-- Name: watchlist uq_watchlist_user_ticker; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT uq_watchlist_user_ticker UNIQUE (user_id, ticker);


--
-- Name: user_interest_sectors user_interest_sectors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_interest_sectors
    ADD CONSTRAINT user_interest_sectors_pkey PRIMARY KEY (id);


--
-- Name: user_refresh_tokens user_refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_refresh_tokens
    ADD CONSTRAINT user_refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: user_refresh_tokens user_refresh_tokens_refresh_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_refresh_tokens
    ADD CONSTRAINT user_refresh_tokens_refresh_token_key UNIQUE (refresh_token);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: watchlist watchlist_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT watchlist_pkey PRIMARY KEY (id);


--
-- Name: idx_action_plans_user_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_action_plans_user_created ON public.action_plans USING btree (user_id, created_at DESC);


--
-- Name: idx_action_plans_user_last_trade; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_action_plans_user_last_trade ON public.action_plans USING btree (user_id, last_trade_id);


--
-- Name: idx_asset_prices_captured_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_asset_prices_captured_at ON public.asset_prices USING btree (captured_at DESC);


--
-- Name: idx_holdings_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_holdings_ticker ON public.holdings USING btree (ticker);


--
-- Name: idx_holdings_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_holdings_user_id ON public.holdings USING btree (user_id);


--
-- Name: idx_portfolio_snapshots_user_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_portfolio_snapshots_user_date ON public.portfolio_snapshots USING btree (user_id, captured_date DESC);


--
-- Name: idx_trade_market_snapshots_trade_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trade_market_snapshots_trade_id ON public.trade_market_snapshots USING btree (trade_id);


--
-- Name: idx_trade_market_snapshots_type_range; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trade_market_snapshots_type_range ON public.trade_market_snapshots USING btree (type, range);


--
-- Name: idx_trade_positions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trade_positions_user_id ON public.trade_positions USING btree (user_id);


--
-- Name: idx_trade_positions_user_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trade_positions_user_ticker ON public.trade_positions USING btree (user_id, ticker);


--
-- Name: idx_trades_position_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trades_position_id ON public.trades USING btree (position_id);


--
-- Name: idx_trades_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trades_ticker ON public.trades USING btree (ticker);


--
-- Name: idx_trades_user_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trades_user_date ON public.trades USING btree (user_id, trade_date DESC);


--
-- Name: idx_trades_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_trades_user_id ON public.trades USING btree (user_id);


--
-- Name: idx_watchlist_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_watchlist_ticker ON public.watchlist USING btree (ticker);


--
-- Name: idx_watchlist_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_watchlist_user_id ON public.watchlist USING btree (user_id);


--
-- Name: uk_provider; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uk_provider ON public.users USING btree (provider, provider_id);


--
-- Name: uq_trade_positions_open_per_ticker; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX uq_trade_positions_open_per_ticker ON public.trade_positions USING btree (user_id, ticker) WHERE ((status)::text = 'OPEN'::text);


--
-- Name: asset_prices asset_prices_ticker_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asset_prices
    ADD CONSTRAINT asset_prices_ticker_fkey FOREIGN KEY (ticker) REFERENCES public.assets(ticker) ON DELETE CASCADE;


--
-- Name: action_plans fk_action_plans_trade; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.action_plans
    ADD CONSTRAINT fk_action_plans_trade FOREIGN KEY (last_trade_id) REFERENCES public.trades(id) ON DELETE RESTRICT;


--
-- Name: action_plans fk_action_plans_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.action_plans
    ADD CONSTRAINT fk_action_plans_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: holdings fk_holdings_asset; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holdings
    ADD CONSTRAINT fk_holdings_asset FOREIGN KEY (ticker) REFERENCES public.assets(ticker);


--
-- Name: holdings fk_holdings_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.holdings
    ADD CONSTRAINT fk_holdings_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_interest_sectors fk_interest_sector; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_interest_sectors
    ADD CONSTRAINT fk_interest_sector FOREIGN KEY (sector_id) REFERENCES public.sectors(id) ON DELETE CASCADE;


--
-- Name: user_interest_sectors fk_interest_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_interest_sectors
    ADD CONSTRAINT fk_interest_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: portfolio_snapshots fk_portfolio_snapshots_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_snapshots
    ADD CONSTRAINT fk_portfolio_snapshots_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: sector_summaries fk_sector_summary_sector; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sector_summaries
    ADD CONSTRAINT fk_sector_summary_sector FOREIGN KEY (sector_id) REFERENCES public.sectors(id) ON DELETE CASCADE;


--
-- Name: trade_market_snapshots fk_snapshots_trade; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_market_snapshots
    ADD CONSTRAINT fk_snapshots_trade FOREIGN KEY (trade_id) REFERENCES public.trades(id) ON DELETE CASCADE;


--
-- Name: trade_positions fk_trade_positions_asset; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_positions
    ADD CONSTRAINT fk_trade_positions_asset FOREIGN KEY (ticker) REFERENCES public.assets(ticker);


--
-- Name: trade_positions fk_trade_positions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_positions
    ADD CONSTRAINT fk_trade_positions_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: trade_results fk_trade_results_trade; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trade_results
    ADD CONSTRAINT fk_trade_results_trade FOREIGN KEY (trade_id) REFERENCES public.trades(id) ON DELETE CASCADE;


--
-- Name: trades fk_trades_asset; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT fk_trades_asset FOREIGN KEY (ticker) REFERENCES public.assets(ticker);


--
-- Name: trades fk_trades_position; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT fk_trades_position FOREIGN KEY (position_id) REFERENCES public.trade_positions(id) ON DELETE RESTRICT;


--
-- Name: trades fk_trades_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT fk_trades_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_refresh_tokens fk_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_refresh_tokens
    ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: watchlist fk_watchlist_asset; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT fk_watchlist_asset FOREIGN KEY (ticker) REFERENCES public.assets(ticker);


--
-- Name: watchlist fk_watchlist_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watchlist
    ADD CONSTRAINT fk_watchlist_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: ticker_news ticker_news_ticker_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticker_news
    ADD CONSTRAINT ticker_news_ticker_id_fkey FOREIGN KEY (ticker_id) REFERENCES public.tickers(id) ON DELETE CASCADE;


--
-- Name: tickers tickers_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickers
    ADD CONSTRAINT tickers_sector_id_fkey FOREIGN KEY (sector_id) REFERENCES public.sectors(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict C4340EfjMvb4JP3RrKfDv5uPLocctVrP8JuRKLMfOlBr1BEzLy2QtU47DXW2sO9

