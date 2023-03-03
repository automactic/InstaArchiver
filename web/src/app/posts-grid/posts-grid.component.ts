import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable, BehaviorSubject } from 'rxjs';
import { filter, combineLatestWith, switchMap, tap, map } from 'rxjs/operators';

import { PostService, ListPostsResponse, Post } from '../services/post.service';


@Component({
  selector: 'app-posts-grid',
  templateUrl: './posts-grid.component.html',
  styleUrls: ['./posts-grid.component.scss']
})
export class PostsGridComponent {
  username?: string
  year?: string
  month?: string
  response$: Observable<ListPostsResponse>
  selectedPost$: Observable<Post>
  postService: PostService;

  constructor(private route: ActivatedRoute, postService: PostService) {
    this.postService = postService
    this.response$ = this.route.paramMap.pipe(
      combineLatestWith(this.route.queryParamMap),
      filter(([params, queryParams]) => {
        return (
          this.username == undefined || 
          params.get('username') != this.username || 
          queryParams.get('year') != this.year ||
          queryParams.get('month') != this.month
        )
      }),
      tap(([params, queryParams]) => {
        this.username = params.get('username') ?? undefined
        this.year = queryParams.get('year') ?? undefined
        this.month = queryParams.get('month') ?? undefined
      }),
      switchMap(_ => {
        return postService.list(0, 100, this.username, this.year, this.month)
      })
    )
    this.selectedPost$ = this.route.queryParamMap.pipe(
      switchMap(queryParams => {
        let selectedShortcode = queryParams.get('selected')
        if (selectedShortcode) {
          let cachedPost = this.postService.getCached(selectedShortcode)
          if (cachedPost) {
            return new BehaviorSubject<Post>(cachedPost)
          } else {
            return this.postService.getPost(selectedShortcode)
          }
        } else {
          return new Observable<Post>()
        }
      })
    )
  }
}
