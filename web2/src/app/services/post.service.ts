import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { tap } from 'rxjs';

import { environment } from '../../environments/environment';


export interface Post {
  shortcode: string
  username: string
  timestamp: Date
  type: string
  caption: string
	items: PostItem[]
}

export interface PostItem {
  index: number
  type: string
  duration: number
  filename: string
  thumb_image_filename: string
}

export interface ListPostsResponse {
  posts: Post[]
  limit: number
  offset: number
  count: number
}


@Injectable({
  providedIn: 'root'
})
export class PostService {
  private posts = new Map<string, Post>()

  constructor(
    private httpClient: HttpClient,
    private route: ActivatedRoute,
    private router: Router, 
  ) { }

  list(offset: number = 0, limit: number = 10, username?: string, year?: string, month?: string) {
    let url = `${environment.apiRoot}/api/posts/`;
    let params: Record<string, string> = { offset: String(offset), limit: String(limit) };
    if (username) { params['username'] = username }
    if (year && month) {
      params['start_time'] = new Date(+year, +month - 1, 1).toISOString();
      params['end_time'] = new Date(+month == 12 ? +year + 1 : +year, +month == 12 ? 0 : +month, 1).toISOString();
    } else if ( year && !month ) {
      params['start_time'] = new Date(+year, 0, 1).toISOString();
      params['end_time'] = new Date(+year + 1, 0, 1).toISOString();
    }
    return this.httpClient.get<ListPostsResponse>(url, {params: params}).pipe(
      tap(response => {
        response.posts.forEach(post => {
          this.posts.set(post.shortcode, post)
        })
      })
    );
  }

  get(shortcode: string) {
    return this.posts.get(shortcode)
  }

  deletePost(shortcode: string) {
    let url = `${environment.apiRoot}/api/posts/${shortcode}/`;
    return this.httpClient.delete(url)
  }

  deleteItem(shortcode: string, itemIndex: number) {
    let url = `${environment.apiRoot}/api/posts/${shortcode}/${itemIndex}/`;
    return this.httpClient.delete(url)
    // return this.httpClient.delete(url).pipe(
    //   tap(_ => {
    //     let post = this.posts.get(shortcode)
    //     if (post?.items.length == 1) {
    //       this.posts.delete(shortcode)
    //       this.shortcodes.forEach((item, index, array) => {
    //         if (item == shortcode) {
    //           array.splice(index, 1)
    //         }
    //       })
    //       this.router.navigate([], { 
    //         relativeTo: this.route, 
    //         queryParams: { selected: null }, 
    //         queryParamsHandling: 'merge' 
    //       })
    //     } else {
          // post?.items.forEach((item, index, array) => {
          //   if (item.index == itemIndex) {
          //     array.splice(index, 1)
          //   }
          // })
    //     }
    //   })
    // )
  }

  getMediaPath(username: string, filename: string): string {
    return `${environment.apiRoot}/media/posts/${username}/${filename}`;
  }

  getPosterPath(username: string, filename: string): string {
    return `${environment.apiRoot}/media/thumb_images/${username}/${filename}`;
  }
}