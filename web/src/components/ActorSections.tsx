import { AtSign, CalendarDays, Camera, ExternalLink, Globe2, Radio, Search } from "lucide-react";

import type { Actor, EventCategory, EventItem, Platform, SnsPost } from "../types";

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
  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-sm">
      <h2 className="text-sm font-semibold text-ink">Dossier</h2>
      <dl className="mt-3 space-y-2 text-sm">
        <Row label="所属" value={actor.agency} />
        <Row label="生日" value={actor.birthday} />
        <Row label="出身" value={actor.birthplace} />
      </dl>
      <div className="mt-4 flex flex-wrap gap-2">
        {actor.socialLinks.map((link) => {
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
          <p className="mt-4 max-w-2xl text-sm leading-7 text-[#d4dde6]">
            {actor.agency} 所属。代表角色、活动时间线和 SNS 动态会从配置与 API 汇聚到同一面板。
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            {actor.roles.slice(0, 4).map((role) => (
              <span key={`${role.title}-${role.character}`} className="rounded-md border border-white/[0.12] bg-white/[0.08] px-3 py-1.5 text-xs text-[#edf5f7]">
                {role.title} / {role.character}
              </span>
            ))}
          </div>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <Metric label="代表作" value={`${actor.roles.length}`} />
          <Metric label="兴趣" value={`${actor.hobbies.length}`} />
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
  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <CalendarDays className="h-5 w-5 text-accent" />
          Event Timeline
        </h2>
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
      <div className="mt-5 space-y-3">
        {props.events.length ? props.events.map((event) => <EventRow key={event.id} event={event} />) : <p className="text-sm text-moss">暂无匹配活动。</p>}
      </div>
    </section>
  );
}

export function SnsPanel({ posts }: { posts: SnsPost[] }) {
  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-sm">
      <h2 className="flex items-center gap-2 text-lg font-semibold">
        <Radio className="h-5 w-5 text-accent" />
        SNS Feed
      </h2>
      <div className="mt-4 space-y-3">
        {posts.length ? posts.map((post) => <SnsRow key={post.id} post={post} />) : <p className="text-sm text-moss">暂无可展示动态。</p>}
      </div>
    </section>
  );
}

function EventRow({ event }: { event: EventItem }) {
  return (
    <article className="rounded-md border border-line bg-[#fbfcfd] px-4 py-3 shadow-[0_1px_0_rgba(17,24,39,0.03)]">
      <div className="flex flex-wrap items-center gap-2 text-xs text-moss">
        <time className="rounded bg-white px-2 py-1">{event.date}</time>
        <span className="rounded bg-[#eaf6f2] px-2 py-1 text-[#356d62]">{categoryLabels[event.category]}</span>
        {event.venue ? <span className="rounded bg-white px-2 py-1">{event.venue}</span> : null}
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
  return (
    <a className="block rounded-md border border-line bg-[#fbfcfd] p-4 transition hover:border-accent hover:bg-white" href={post.url} target="_blank" rel="noreferrer">
      <div className="flex items-center justify-between gap-3 text-xs text-moss">
        <span className="inline-flex items-center gap-1">
          <Icon className="h-4 w-4" />
          {post.platform.toUpperCase()}
        </span>
        <time>{new Date(post.postedAt).toLocaleDateString("zh-CN")}</time>
      </div>
      <p className="mt-2 text-sm leading-6">{post.text}</p>
    </a>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3 border-b border-line pb-2">
      <dt className="text-moss">{label}</dt>
      <dd className="text-right font-medium">{value}</dd>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-white/[0.12] bg-white/[0.08] p-3">
      <p className="text-xs text-[#9adfcb]">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}
