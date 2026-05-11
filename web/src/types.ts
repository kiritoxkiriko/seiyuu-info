export type Platform = "x" | "instagram" | "youtube" | "website";
export type EventCategory = "live" | "stage" | "talk" | "release" | "broadcast" | "other";

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
  date: string;
  category: EventCategory;
  venue?: string | null;
  url?: string | null;
  source: string;
}

export interface SnsPost {
  id: string;
  actorId: string;
  platform: Platform;
  postedAt: string;
  text: string;
  url: string;
  kind: "original" | "repost" | "reply" | "quote" | "story";
  mediaUrls: string[];
}

export interface ActorDetail {
  actor: Actor;
  events: EventItem[];
  sns: SnsPost[];
}
