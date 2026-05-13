import { AtSign, CalendarDays, Camera, ChevronDown, ChevronUp, Download, ExternalLink, Globe2, ImageIcon, Languages, Radio, Search, X } from "lucide-react";
import { Fragment, useEffect, useMemo, useState } from "react";

import type { Actor, EventCategory, EventItem, Language, Platform, SnsPost } from "../types";

export const categoryLabels: Record<EventCategory | "all", string> = {
  all: "全部",
  live: "Live",
  stage: "舞台",
  talk: "Talk",
  release: "发售",
  broadcast: "放送",
  other: "其他",
};

const platformIcons: Record<Platform, typeof Globe2> = {
  x: AtSign,
  instagram: Camera,
  youtube: Radio,
  website: Globe2,
};

const COLLAPSED_TEXT_LENGTH = 140;
const EVENT_PAGE_SIZE = 6;
const SNS_PAGE_SIZE = 6;
const URL_PATTERN = /(https?:\/\/[^\s]+)/g;
const snsFilterLabels = {
  all: "全部",
  media: "带图片",
  text: "仅文字",
} as const;

export function ActorTabs({ actors, activeId, onSelect }: { actors: Actor[]; activeId: string; onSelect: (id: string) => void }) {
  return (
    <nav className="rounded-lg border border-line bg-white p-2 shadow-sm">
      <div className="px-2 pb-2 pt-1 text-xs font-semibold uppercase tracking-[0.18em] text-moss">cast list</div>
      {actors.map((actor) => (
        <button
          key={actor.id}
          className={`mb-2 flex w-full items-center gap-3 rounded-md border px-3 py-3 text-left transition last:mb-0 ${
            actor.id === activeId ? "border-accent bg-[#fff6f4] shadow-sm" : "border-transparent hover:border-line hover:bg-[#f7fafb]"
          }`}
          onClick={() => onSelect(actor.id)}
          type="button"
        >
          <img className="h-12 w-12 rounded-md object-cover object-top" src={actor.officialPhoto.url} alt={actor.officialPhoto.alt} />
          <span>
            <span className="block text-sm font-semibold text-ink">{actor.name}</span>
            <span className="block text-xs text-moss">{actor.agency}</span>
          </span>
        </button>
      ))}
    </nav>
  );
}

export function ProfileSummary({ actor }: { actor: Actor }) {
  const visibleLinks = actor.socialLinks.filter((link) => link.platform !== "instagram");

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold text-ink">Dossier</h2>
      <dl className="mt-3 space-y-2 text-sm">
        <Row label="所属" value={actor.agency} />
        <Row label="生日" value={actor.birthday} />
        <Row label="出身" value={actor.birthplace} />
      </dl>
      <div className="mt-4 flex flex-wrap gap-2">
        {visibleLinks.map((link) => {
          const Icon = platformIcons[link.platform];
          return (
            <a
              key={link.url}
              className="inline-flex items-center gap-1 rounded-md border border-line bg-[#f7fafb] px-2.5 py-1.5 text-xs hover:border-accent hover:text-accent"
              href={link.url}
              rel="noreferrer"
              target="_blank"
            >
              <Icon className="h-3.5 w-3.5" />
              {link.label}
            </a>
          );
        })}
      </div>
    </section>
  );
}

export function LanguageSwitch({ language, onChange }: { language: Language; onChange: (language: Language) => void }) {
  return (
    <section className="flex items-center justify-between rounded-lg border border-line bg-white px-4 py-3 shadow-sm">
      <div className="flex items-center gap-2 text-sm font-semibold text-ink">
        <Languages className="h-4 w-4 text-accent" />
        显示语言
      </div>
      <div className="grid grid-cols-2 rounded-md border border-line bg-[#f7fafb] p-1 text-sm">
        {[
          ["original", "原文"],
          ["zh", "中文"],
        ].map(([value, label]) => (
          <button
            key={value}
            className={`rounded px-3 py-1.5 transition ${
              language === value ? "bg-navy text-white shadow-sm" : "text-moss hover:text-ink"
            }`}
            onClick={() => onChange(value as Language)}
            type="button"
          >
            {label}
          </button>
        ))}
      </div>
    </section>
  );
}

export function Hero({ actor, loading }: { actor: Actor; loading: boolean }) {
  return (
    <section className="grid overflow-hidden rounded-lg border border-[#252d3c] bg-navy text-white shadow-lg lg:grid-cols-[minmax(260px,360px)_1fr]">
      <div className="relative min-h-[380px] bg-[#0f141d]">
        <img className="h-full min-h-[380px] w-full object-cover object-top opacity-95" src={actor.officialPhoto.url} alt={actor.officialPhoto.alt} />
        <div className="absolute inset-x-0 bottom-0 bg-[#111827]/[0.88] px-4 py-3 text-xs text-[#d9e4ec]">{actor.officialPhoto.source}</div>
      </div>
      <div className="flex flex-col justify-between p-5 sm:p-8">
        <div>
          <div className="flex flex-wrap items-center gap-2 text-sm text-[#9adfcb]">
            <span>{actor.kana}</span>
            <span>/</span>
            <span>{actor.romanized}</span>
          </div>
          <h2 className="mt-2 text-4xl font-semibold tracking-normal sm:text-6xl">{actor.name}</h2>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-[#d4dde6]">{profileIntro(actor)}</p>
          <div className="mt-5 flex flex-wrap gap-2">
            {actor.roles.slice(0, 4).map((role) => (
              <span key={`${role.title}-${role.character}`} className="rounded-md border border-white/[0.12] bg-white/[0.08] px-3 py-2 text-xs text-[#edf5f7]">
                <span className="block font-semibold">{role.character}</span>
                <span className="mt-0.5 block text-[#b8c7d3]">{role.title}</span>
              </span>
            ))}
          </div>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <Metric label="代表作" value={`${actor.roles.length}`} />
          <TraitCard label="兴趣" items={actor.hobbies} />
          <Metric label="状态" value={loading ? "同步中" : "已载入"} />
        </div>
      </div>
    </section>
  );
}

export function EventsPanel(props: {
  events: EventItem[];
  category: EventCategory | "all";
  query: string;
  onCategoryChange: (value: EventCategory | "all") => void;
  onQueryChange: (value: string) => void;
}) {
  const [upcomingPage, setUpcomingPage] = useState(1);
  const [pastPage, setPastPage] = useState(1);
  const today = useMemo(() => new Date().toLocaleDateString("en-CA"), []);
  const upcomingEvents = useMemo(
    () => props.events.filter((event) => isUpcomingEvent(event, today)).toSorted((a, b) => compareEventDate(a, b, "asc")),
    [props.events, today],
  );
  const pastEvents = useMemo(
    () => props.events.filter((event) => !isUpcomingEvent(event, today)).toSorted((a, b) => compareEventDate(a, b, "desc")),
    [props.events, today],
  );
  const visibleUpcomingEvents = useMemo(
    () => upcomingEvents.slice((upcomingPage - 1) * EVENT_PAGE_SIZE, upcomingPage * EVENT_PAGE_SIZE),
    [upcomingEvents, upcomingPage],
  );
  const visiblePastEvents = useMemo(
    () => pastEvents.slice((pastPage - 1) * EVENT_PAGE_SIZE, pastPage * EVENT_PAGE_SIZE),
    [pastEvents, pastPage],
  );
  const upcomingTotalPages = Math.max(1, Math.ceil(upcomingEvents.length / EVENT_PAGE_SIZE));
  const pastTotalPages = Math.max(1, Math.ceil(pastEvents.length / EVENT_PAGE_SIZE));

  useEffect(() => {
    setUpcomingPage(1);
    setPastPage(1);
  }, [props.events]);

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <CalendarDays className="h-5 w-5 text-accent" />
            Event Timeline
          </h2>
          {props.events.length ? <span className="text-xs text-moss">{props.events.length} 条</span> : null}
        </div>
        <label className="flex items-center gap-2 rounded-md border border-line bg-[#f7fafb] px-3 py-2 text-sm">
          <Search className="h-4 w-4 text-moss" />
          <input
            aria-label="搜索活动"
            className="w-full bg-transparent outline-none placeholder:text-[#8a99a8]"
            placeholder="搜索 event"
            value={props.query}
            onChange={(event) => props.onQueryChange(event.target.value)}
          />
        </label>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {(Object.keys(categoryLabels) as Array<EventCategory | "all">).map((key) => (
          <button
            key={key}
            className={`rounded-md border px-3 py-1.5 text-xs transition ${
              props.category === key ? "border-accent bg-[#fff6f4] text-accent" : "border-line bg-[#f7fafb] hover:border-accent"
            }`}
            onClick={() => props.onCategoryChange(key)}
            type="button"
          >
            {categoryLabels[key]}
          </button>
        ))}
      </div>
      <div className="mt-5 space-y-6">
        <EventBucket
          title="即将开始"
          tone="upcoming"
          today={today}
          events={visibleUpcomingEvents}
          totalCount={upcomingEvents.length}
          page={upcomingPage}
          totalPages={upcomingTotalPages}
          onPageChange={setUpcomingPage}
          emptyText="暂无即将开始的活动。"
        />
        <EventBucket
          title="已结束"
          tone="past"
          today={today}
          events={visiblePastEvents}
          totalCount={pastEvents.length}
          page={pastPage}
          totalPages={pastTotalPages}
          onPageChange={setPastPage}
          emptyText="暂无已结束的活动。"
        />
      </div>
    </section>
  );
}

export function SnsPanel({ posts }: { posts: SnsPost[] }) {
  const [filter, setFilter] = useState<keyof typeof snsFilterLabels>("all");
  const [page, setPage] = useState(1);
  const filteredPosts = useMemo(() => {
    if (filter === "media") {
      return posts.filter((post) => post.mediaUrls.length > 0);
    }
    if (filter === "text") {
      return posts.filter((post) => post.mediaUrls.length === 0);
    }
    return posts;
  }, [filter, posts]);
  const visiblePosts = useMemo(() => filteredPosts.slice((page - 1) * SNS_PAGE_SIZE, page * SNS_PAGE_SIZE), [filteredPosts, page]);
  const totalPages = Math.max(1, Math.ceil(filteredPosts.length / SNS_PAGE_SIZE));

  useEffect(() => {
    setPage(1);
  }, [filter, posts]);

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <Radio className="h-5 w-5 text-accent" />
          SNS Feed
        </h2>
        {filteredPosts.length ? <span className="text-xs text-moss">{filteredPosts.length} 条 / 第 {page} 页</span> : null}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {(Object.keys(snsFilterLabels) as Array<keyof typeof snsFilterLabels>).map((key) => (
          <button
            key={key}
            className={`rounded-md border px-3 py-1.5 text-xs transition ${
              filter === key ? "border-accent bg-[#fff6f4] text-accent" : "border-line bg-[#f7fafb] hover:border-accent"
            }`}
            onClick={() => setFilter(key)}
            type="button"
          >
            {snsFilterLabels[key]}
          </button>
        ))}
      </div>
      <div className="mt-4 space-y-3">
        {visiblePosts.length ? visiblePosts.map((post) => <SnsRow key={post.id} post={post} />) : <p className="text-sm text-moss">暂无可展示动态。</p>}
      </div>
      {totalPages > 1 ? <Pagination page={page} totalPages={totalPages} onPageChange={setPage} ariaLabel="SNS 分页" /> : null}
    </section>
  );
}

function EventBucket({
  title,
  tone,
  today,
  events,
  totalCount,
  page,
  totalPages,
  onPageChange,
  emptyText,
}: {
  title: string;
  tone: "upcoming" | "past";
  today: string;
  events: EventItem[];
  totalCount: number;
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  emptyText: string;
}) {
  return (
    <section className="border-t border-line pt-4 first:border-t-0 first:pt-0">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-ink">{title}</h3>
          <span
            className={`rounded px-2 py-1 text-xs ${
              tone === "upcoming" ? "bg-[#fff1e8] text-[#bf5f1f]" : "bg-[#edf1f4] text-[#5e6b76]"
            }`}
          >
            {totalCount} 条
          </span>
        </div>
        {totalPages > 1 ? <span className="text-xs text-moss">第 {page} 页</span> : null}
      </div>
      <div className="mt-3 space-y-3">
        {events.length ? events.map((event) => <EventRow key={event.id} event={event} tone={tone} today={today} />) : <p className="text-sm text-moss">{emptyText}</p>}
      </div>
      {totalPages > 1 ? <Pagination page={page} totalPages={totalPages} onPageChange={onPageChange} ariaLabel={`${title} 分页`} /> : null}
    </section>
  );
}

function Pagination({
  page,
  totalPages,
  onPageChange,
  ariaLabel,
}: {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  ariaLabel: string;
}) {
  return (
    <nav className="mt-4 flex items-center justify-between gap-2 border-t border-line pt-3 text-sm" aria-label={ariaLabel}>
      <button
        className="rounded-md border border-line bg-white px-3 py-1.5 text-xs font-medium disabled:cursor-not-allowed disabled:opacity-40 hover:enabled:border-accent hover:enabled:text-accent"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
        type="button"
      >
        上一页
      </button>
      <div className="flex items-center gap-1">
        {Array.from({ length: totalPages }, (_, index) => index + 1).map((item) => (
          <button
            key={item}
            className={`h-8 w-8 rounded-md border text-xs font-medium ${
              item === page ? "border-navy bg-navy text-white" : "border-line bg-white hover:border-accent hover:text-accent"
            }`}
            onClick={() => onPageChange(item)}
            type="button"
          >
            {item}
          </button>
        ))}
      </div>
      <button
        className="rounded-md border border-line bg-white px-3 py-1.5 text-xs font-medium disabled:cursor-not-allowed disabled:opacity-40 hover:enabled:border-accent hover:enabled:text-accent"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
        type="button"
      >
        下一页
      </button>
    </nav>
  );
}

function EventRow({ event, tone, today }: { event: EventItem; tone: "upcoming" | "past"; today: string }) {
  const countdown = tone === "upcoming" ? formatCountdown(event.date, today) : null;
  const calendarUrl = countdown ? buildIcsDataUrl(event) : null;
  const calendarFilename = countdown ? buildIcsFilename(event) : null;
  const venueMapUrl = event.venue ? buildGoogleMapsUrl(event.venue) : null;
  const mappableVenue = event.venue ? isMappableVenue(event.venue) : false;
  return (
    <article className="rounded-md border border-line bg-[#fbfcfd] px-4 py-3 shadow-[0_1px_0_rgba(17,24,39,0.03)]">
      <div className="flex flex-wrap items-center gap-2 text-xs text-moss">
        <time className="rounded bg-white px-2 py-1">{event.date}</time>
        <span className="rounded bg-[#eaf6f2] px-2 py-1 text-[#356d62]">{categoryLabels[event.category]}</span>
        {tone === "past" ? <span className="rounded bg-[#edf1f4] px-2 py-1 text-[#5e6b76]">已结束</span> : null}
        {countdown && calendarUrl ? (
          <a
            className="rounded bg-[#fff7db] px-2 py-1 text-[#9b6b13] hover:bg-[#fde9a9] hover:text-[#7a5104]"
            href={calendarUrl}
            download={calendarFilename ?? `${event.id}.ics`}
            title="下载 iCalendar 日程"
          >
            {countdown}
          </a>
        ) : null}
        {event.venue ? (
          mappableVenue && venueMapUrl ? (
            <a
              className="rounded bg-white px-2 py-1 hover:border-accent hover:text-accent"
              href={venueMapUrl}
              rel="noreferrer"
              target="_blank"
              title="在 Google 地图中打开"
            >
              {event.venue}
            </a>
          ) : (
            <span className="rounded bg-white px-2 py-1">{event.venue}</span>
          )
        ) : null}
      </div>
      <a className="mt-2 inline-flex items-center gap-1 font-semibold hover:text-accent" href={event.url ?? "#"} target="_blank" rel="noreferrer">
        {event.title}
        <ExternalLink className="h-3.5 w-3.5" />
      </a>
    </article>
  );
}

function SnsRow({ post }: { post: SnsPost }) {
  const Icon = platformIcons[post.platform];
  const [expanded, setExpanded] = useState(false);
  const [activeImage, setActiveImage] = useState<string | null>(null);
  const detailText = post.detailText ?? post.text;
  const hasMedia = post.mediaUrls.length > 0;
  const needsTextCollapse = detailText.length > COLLAPSED_TEXT_LENGTH;
  const canExpand = needsTextCollapse || hasMedia || detailText !== post.text;
  const visibleText = expanded || !needsTextCollapse ? detailText : truncateTextPreservingUrls(detailText, COLLAPSED_TEXT_LENGTH);
  return (
    <article className="rounded-md border border-line bg-[#fbfcfd] p-4 transition hover:border-accent hover:bg-white">
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-moss">
        <span className="flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1">
            <Icon className="h-4 w-4" />
            {post.platform.toUpperCase()}
          </span>
          {hasMedia ? (
            <span className="inline-flex items-center gap-1 rounded bg-[#eaf6f2] px-2 py-1 text-[#356d62]">
              <ImageIcon className="h-3.5 w-3.5" />
              含图片
            </span>
          ) : null}
        </span>
        <time>{new Date(post.postedAt).toLocaleDateString("zh-CN")}</time>
      </div>
      <div className="mt-2 text-sm leading-6">{renderPostText(visibleText)}</div>
      {expanded && hasMedia ? <TweetMedia urls={post.mediaUrls} onOpen={setActiveImage} /> : null}
      <div className="mt-3 flex items-center justify-between gap-3">
        {canExpand ? (
          <button
            className="inline-flex items-center gap-1 rounded-md border border-line bg-white px-2.5 py-1.5 text-xs font-medium hover:border-accent hover:text-accent"
            onClick={() => setExpanded((value) => !value)}
            type="button"
          >
            {expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            {expanded ? "收起" : hasMedia ? "展开全文与图片" : "展开全文"}
          </button>
        ) : (
          <span />
        )}
        <a className="inline-flex items-center gap-1 text-xs font-medium text-accent hover:underline" href={post.url} target="_blank" rel="noreferrer">
          打开原文
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
      {activeImage ? <ImageLightbox url={activeImage} onClose={() => setActiveImage(null)} /> : null}
    </article>
  );
}

function renderPostText(text: string) {
  const lines = text.split("\n");
  return lines.map((line, lineIndex) => (
    <Fragment key={`${lineIndex}-${line}`}>
      {linkifyLine(line)}
      {lineIndex < lines.length - 1 ? <br /> : null}
    </Fragment>
  ));
}

function linkifyLine(line: string) {
  const parts = line.split(URL_PATTERN);
  return parts.map((part, index) => {
    if (!part) {
      return null;
    }
    if (isUrl(part)) {
      return (
        <a
          key={`${part}-${index}`}
          className="break-all text-accent underline decoration-accent/40 underline-offset-2 hover:text-[#c5542f]"
          href={part}
          rel="noreferrer"
          target="_blank"
        >
          {part}
        </a>
      );
    }
    return <Fragment key={`${part}-${index}`}>{part}</Fragment>;
  });
}

function truncateTextPreservingUrls(text: string, maxLength: number) {
  if (text.length <= maxLength) {
    return text;
  }

  let cutoff = maxLength;
  for (const match of text.matchAll(URL_PATTERN)) {
    const start = match.index ?? 0;
    const url = match[0];
    const end = start + url.length;
    if (cutoff > start && cutoff < end) {
      cutoff = end;
      break;
    }
  }

  return `${text.slice(0, cutoff).trimEnd()}...`;
}

function isUrl(value: string) {
  return /^https?:\/\//.test(value);
}

function isUpcomingEvent(event: EventItem, today: string) {
  return /^\d{4}-\d{2}-\d{2}$/.test(event.date) && event.date >= today;
}

function compareEventDate(a: EventItem, b: EventItem, direction: "asc" | "desc") {
  const result = a.date.localeCompare(b.date);
  return direction === "asc" ? result : -result;
}

function formatCountdown(eventDate: string, today: string) {
  const target = parseIsoDate(eventDate);
  const current = parseIsoDate(today);
  if (!target || !current) {
    return null;
  }

  const diffDays = Math.ceil((target.getTime() - current.getTime()) / 86400000);
  if (diffDays <= 0) {
    return "今天开始";
  }
  if (diffDays < 30) {
    return `还剩${diffDays}天`;
  }

  const months =
    (target.getFullYear() - current.getFullYear()) * 12 +
    (target.getMonth() - current.getMonth()) -
    (target.getDate() < current.getDate() ? 1 : 0);

  return `还剩${Math.max(1, months)}个月`;
}

function parseIsoDate(value: string) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) {
    return null;
  }
  return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
}

function buildIcsDataUrl(event: EventItem) {
  const target = parseIsoDate(event.date);
  if (!target) {
    return null;
  }
  const end = new Date(target);
  end.setDate(end.getDate() + 1);

  const content = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//nsy-station//Event Calendar//ZH",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "BEGIN:VEVENT",
    `UID:${escapeIcsText(event.id)}@nsy-station`,
    `DTSTAMP:${formatUtcTimestamp(new Date())}`,
    `DTSTART;VALUE=DATE:${formatCalendarDate(target)}`,
    `DTEND;VALUE=DATE:${formatCalendarDate(end)}`,
    `SUMMARY:${escapeIcsText(event.title)}`,
    `LOCATION:${escapeIcsText(event.venue ?? "")}`,
    `DESCRIPTION:${escapeIcsText(event.url ?? "")}`,
    "END:VEVENT",
    "END:VCALENDAR",
  ].join("\r\n");

  return `data:text/calendar;charset=utf-8,${encodeURIComponent(content)}`;
}

function buildIcsFilename(event: EventItem) {
  return `${event.id}.ics`;
}

function formatCalendarDate(value: Date) {
  const year = value.getFullYear();
  const month = `${value.getMonth() + 1}`.padStart(2, "0");
  const day = `${value.getDate()}`.padStart(2, "0");
  return `${year}${month}${day}`;
}

function formatUtcTimestamp(value: Date) {
  const year = value.getUTCFullYear();
  const month = `${value.getUTCMonth() + 1}`.padStart(2, "0");
  const day = `${value.getUTCDate()}`.padStart(2, "0");
  const hours = `${value.getUTCHours()}`.padStart(2, "0");
  const minutes = `${value.getUTCMinutes()}`.padStart(2, "0");
  const seconds = `${value.getUTCSeconds()}`.padStart(2, "0");
  return `${year}${month}${day}T${hours}${minutes}${seconds}Z`;
}

function escapeIcsText(value: string) {
  return value
    .replace(/\\/g, "\\\\")
    .replace(/\n/g, "\\n")
    .replace(/,/g, "\\,")
    .replace(/;/g, "\\;");
}

function buildGoogleMapsUrl(venue: string) {
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(venue)}`;
}

function isMappableVenue(venue: string) {
  return !/^(online|youtube|未設定|未定)$/i.test(venue.trim());
}

function TweetMedia({ urls, onOpen }: { urls: string[]; onOpen: (url: string) => void }) {
  return (
    <div className={`mt-3 grid gap-2 ${urls.length > 1 ? "grid-cols-2" : "grid-cols-1"}`}>
      {urls.map((url, index) => (
        <button
          key={url}
          className="group relative overflow-hidden rounded-md border border-line bg-white text-left"
          onClick={() => onOpen(url)}
          type="button"
        >
          <img className="h-44 w-full object-cover transition group-hover:scale-[1.02]" src={url} alt={`推文图片 ${index + 1}`} loading="lazy" />
          <span className="absolute bottom-2 right-2 rounded bg-[#111827]/75 px-2 py-1 text-xs font-medium text-white">查看大图</span>
        </button>
      ))}
    </div>
  );
}

function ImageLightbox({ url, onClose }: { url: string; onClose: () => void }) {
  const downloadUrl = highQualityImageUrl(url);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#111827]/85 p-4" role="dialog" aria-modal="true">
      <div className="max-h-full w-full max-w-5xl">
        <div className="mb-3 flex items-center justify-end gap-2">
          <a
            className="inline-flex items-center gap-1 rounded-md bg-white px-3 py-2 text-sm font-medium text-ink hover:text-accent"
            href={downloadUrl}
            target="_blank"
            rel="noreferrer"
            download
          >
            <Download className="h-4 w-4" />
            下载高清
          </a>
          <button className="inline-flex items-center gap-1 rounded-md bg-white px-3 py-2 text-sm font-medium text-ink hover:text-accent" onClick={onClose} type="button">
            <X className="h-4 w-4" />
            关闭
          </button>
        </div>
        <button className="block max-h-[82vh] w-full overflow-hidden rounded-lg bg-black" onClick={onClose} type="button">
          <img className="mx-auto max-h-[82vh] w-auto max-w-full object-contain" src={downloadUrl} alt="推文大图" />
        </button>
      </div>
    </div>
  );
}

function highQualityImageUrl(url: string) {
  if (!url.includes("pbs.twimg.com/media/")) {
    return url;
  }
  const [base] = url.split("?");
  return `${base}?format=jpg&name=orig`;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3 border-b border-line pb-2">
      <dt className="text-moss">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}

function profileIntro(actor: Actor) {
  if (actor.bio) {
    return actor.bio;
  }
  const specialties = actor.specialties.length ? `特技是 ${actor.specialties.join("、")}。` : "";
  return `${actor.birthplace}出身，${actor.agency}所属。${specialties}`;
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-white/[0.12] bg-white/[0.08] p-3">
      <p className="text-xs text-[#9adfcb]">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}

function TraitCard({ label, items }: { label: string; items: string[] }) {
  return (
    <div className="rounded-md border border-white/[0.12] bg-white/[0.08] p-3">
      <p className="text-xs text-[#9adfcb]">{label}</p>
      <p className="mt-1 max-h-12 overflow-hidden text-sm font-medium leading-6 text-white">{items.length ? items.join(" / ") : "未配置"}</p>
    </div>
  );
}
