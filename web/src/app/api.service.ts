import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class APIService {
  constructor(private httpClient: HttpClient) { }

  savePost(shortcode: string) {
    let url = environment.apiRoot + '/api/posts/from_url/'
    let payload = {'shortcode': shortcode}
    this.httpClient.post(url, payload).subscribe(data => {
      console.log(data);
    })
    console.log(shortcode)
  }
}
