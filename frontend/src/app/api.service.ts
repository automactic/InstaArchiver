import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class APIService {
  constructor(private httpClient: HttpClient) { }
  // root = 'http://localhost:37500'
  root = ''

  savePost(shortcode: string) {
    let url = this.root + '/api/posts/from_url/'
    let payload = {'shortcode': shortcode}
    this.httpClient.post(url, payload).subscribe(data => {
      console.log(data);
    })
    console.log(shortcode)
  }
}
