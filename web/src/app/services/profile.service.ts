import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';


export interface Profile {
	username: string
	full_name: string
	display_name: string
	biography: string
	auto_archive: boolean
	last_scan?: Date
	image_filename: string
	posts?: PostsSummary
}

export interface PostsSummary {
  count: number
	earliest_time?: Date
	latest_time?: Date
}

export class ProfileConfiguration {
  display_name = ""
  auto_archive = false
}

export interface ListProfilesResponse {
  profiles: Profile[]
  limit: number
  offset: number
  count: number
}

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  profiles: Profile[] = []
  display_names = new Map<string, string>();

  constructor(private httpClient: HttpClient) {
    this.list().subscribe(response_data => {
      this.profiles = response_data.profiles
      response_data.profiles.forEach(profile => {
        this.display_names.set(profile.username, profile.display_name);
      })
    })
  }

  list() {
    let url = `${environment.apiRoot}/api/profiles/`;
    return this.httpClient.get<ListProfilesResponse>(url);
  }

  get(username: string): Observable<Profile> {
    let url = `${environment.apiRoot}/api/profiles/${username}/`;
    return this.httpClient.get<Profile>(url);
  }

  updateConfiguration(username: string, configuration: ProfileConfiguration) {
    let url = `${environment.apiRoot}/api/profiles/${username}/`;
    this.httpClient.patch<Profile>(url, configuration).subscribe(profile => {
      let index = this.profiles.findIndex(( item => {return item.username == profile.username}));
      if (index != -1) {
        this.profiles.splice(index, 1, profile);
      }
      this.display_names.set(profile.username, profile.display_name);
    });
  }

  getProfileImagePath(filename: string): string {
    return `${environment.apiRoot}/media/profile_images/${filename}`;
  }
}
