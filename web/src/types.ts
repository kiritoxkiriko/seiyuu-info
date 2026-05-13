export type Platform = "x" | "instagram" | "youtube" | "website";
export type EventCategory = "live" | "stage" | "talk" | "release" | "broadcast" | "other";
export type Language = "original" | "zh";

export interface Photo {
  url: string;
  alt: string;
  source: string;
}

export interface SocialLink {
  platform: Platform;
  label: string;
  url: string;
}

export interface Role {
  title: string;
  character: string;
}

export interface Actor {
  id: string;
  name: string;
  kana: string;
  romanized: string;
  agency: string;
  birthday: string;
  birthplace: string;
  bio?: string | null;
  profile_url: string;
  officialPhoto: Photo;
  gallery: Photo[];
  specialties: string[];
  hobbies: string[];
  roles: Role[];
  socialLinks: SocialLink[];
  eventernoteUrl?: string;
}

export interface EventItem {
  id: string;
  actorId: string;
  title: string;
  titleZh?: string | null;
  date: string;
  category: EventCategory;
  venue?: string | null;
  venueZh?: string | null;
  url?: string | null;
  source: string;
  language: Language;
}

export interface SnsPost {
  id: string;
  actorId: string;
  platform: Platform;
  postedAt: string;
  text: string;
  textZh?: string | null;
  detailText?: string | null;
  detailTextZh?: string | null;
  url: string;
  kind: "original" | "repost" | "reply" | "quote" | "story";
  mediaUrls: string[];
  language: Language;
}

export interface ActorDetail {
  actor: Actor;
  events: EventItem[];
  sns: SnsPost[];
}
