import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';


export interface Profile {
	username: string
	full_name: string
	display_name: string
	biography: string
  image_filename: string
  counts: {[index: string]: {[index: string]: number}}
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

  constructor(private httpClient: HttpClient) {}

  list() {
    let url = `${environment.apiRoot}/api/profiles/?limit=200`;
    return this.httpClient.get<ListProfilesResponse>(url);
  }

  get(username: string): Observable<Profile> {
    let url = `${environment.apiRoot}/api/profiles/${username}/`;
    return this.httpClient.get<Profile>(url);
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

  getProfileImagePath(filename: string): string {
    return `${environment.apiRoot}/media/profile_images/${filename}`;
  }
}
