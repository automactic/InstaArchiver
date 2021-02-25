import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../environments/environment';
import { Profile } from './entities';
import { Observable } from 'rxjs';


export interface ListProfilesResponse {
  profiles: Profile[]
  limit: number
  offset: number
  count: number
}


@Injectable({
  providedIn: 'root'
})
export class APIService {
  constructor(private httpClient: HttpClient) { }

  savePost(shortcode: string) {
    let url = environment.apiRoot + '/api/posts/from_shortcode/'
    let payload = {'shortcode': shortcode}
    this.httpClient.post(url, payload).subscribe(data => {
      console.log(data);
    })
    console.log(shortcode)
  }

  listProfiles() {
    let url = environment.apiRoot + '/api/profiles/'
    return this.httpClient.get<ListProfilesResponse>(url)
  }

  getProfile(username: string): Observable<Profile> {
    let url = `${environment.apiRoot}/api/profiles/${username}/`;
    return this.httpClient.get<Profile>(url);
  }
}
