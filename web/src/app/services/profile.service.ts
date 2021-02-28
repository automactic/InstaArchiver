import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';


export interface PostsSummary {
  count: number
	earliest_time?: Date
	latest_time?: Date
}

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

  constructor(private httpClient: HttpClient) {
    this.listProfiles().subscribe(data => {
      this.profiles = data.profiles
    })
  }

  listProfiles() {
    let url = `${environment.apiRoot}/api/profiles/`;
    return this.httpClient.get<ListProfilesResponse>(url);
  }

  getProfile(username: string): Observable<Profile> {
    let url = `${environment.apiRoot}/api/profiles/${username}/`;
    return this.httpClient.get<Profile>(url);
  }

  getProfileImagePath(filename: string): string {
    return `${environment.apiRoot}/media/profile_images/${filename}`;
  }
}
