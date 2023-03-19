import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { Task } from '../services/task.service';


export interface Profile {
	username: string
	full_name: string
	display_name: string
	biography: string
  image_filename: string
  first_post_timestamp: Date
  last_post_timestamp: Date
  total_count: number
  counts: {[index: string]: {[index: string]: number}}
}

export interface ListProfilesResponse {
  profiles: Profile[]
  limit: number
  offset: number
  count: number
}

export interface ProfileStats {
  first_post_timestamp: Date
  last_post_timestamp: Date
  total_count: number
  counts: {[index: string]: {[index: string]: number}}
}

export interface ProfileWithDetails {
	username: string
	display_name: string
  biography: string
  stats: ProfileStats
  tasks: Task[]
}

@Injectable({providedIn: 'root'})
export class ProfileService {
  profiles: Profile[] = []
  display_names = new Map<string, string>();

  constructor(private httpClient: HttpClient) {}

  list(search?: string) {
    let url = `${environment.apiRoot}/api/profiles/?limit=200`
    let params: Record<string, string> = {}
    if (search) {
      params['search'] = search
    }
    return this.httpClient.get<ListProfilesResponse>(url, {params: params});
  }

  get(username: string): Observable<ProfileWithDetails> {
    let url = `${environment.apiRoot}/api/profiles/${username}/`;
    return this.httpClient.get<ProfileWithDetails>(url);
  }

  update(username: string, display_name: string) {
    let url = `${environment.apiRoot}/api/profiles/${username}/`;
    let configuration = { display_name: display_name }
    this.httpClient.patch<Profile>(url, configuration).subscribe(profile => {
      let index = this.profiles.findIndex(( item => {return item.username == profile.username}));
      if (index != -1) {
        this.profiles.splice(index, 1, profile);
      }
      this.display_names.set(profile.username, profile.display_name);
    });
  }

  updateDisplayName(username: string, displayName: string): Observable<null> {
    let url = `${environment.apiRoot}/api/profiles/${username}/`;
    let payload = { display_name: displayName }
    return this.httpClient.patch<null>(url, payload)
  }

  getStats(username?: string): Observable<[ProfileStats]> {
    let url = `${environment.apiRoot}/api/stats/`
    let params: Record<string, string> = {}
    if (username) { 
      params['username'] = username 
    }
    return this.httpClient.get<[ProfileStats]>(url, {params: params})
  }

  getProfileImagePath(filename: string): string {
    return `${environment.apiRoot}/media/profile_images/${filename}`;
  }
}
