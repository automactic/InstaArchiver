import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable, BehaviorSubject } from 'rxjs';
import { filter, combineLatestWith, switchMap, map } from 'rxjs/operators';

import { PostService, Post } from '../services/post.service';


@Component({
  selector: 'app-posts-grid',
  templateUrl: './posts-grid.component.html',
  styleUrls: ['./posts-grid.component.scss']
})
export class PostsGridComponent {
  postService: PostService;

  username?: string
  year?: string
  month?: string
  selectedPost$: Observable<Post | null>
  selectedUsername$: Observable<string | null>

  constructor(private route: ActivatedRoute, postService: PostService) {
    this.postService = postService
    this.route.paramMap.pipe(
      combineLatestWith(this.route.queryParamMap),
      filter(([params, queryParams]) => {
        return (
          this.username == undefined || 
          params.get('username') != this.username || 
          queryParams.get('year') != this.year ||
          queryParams.get('month') != this.month
        )
      }),
    ).subscribe(([params, queryParams]) => {
      this.username = params.get('username') ?? undefined
      this.year = queryParams.get('year') ?? undefined
      this.month = queryParams.get('month') ?? undefined
      this.postService.posts.clear()
      this.getNextPage()
    })
    this.selectedPost$ = this.route.queryParamMap.pipe(
      switchMap(queryParams => {
        let selectedShortcode = queryParams.get('selected')
        let post = this.postService.posts.get(selectedShortcode ?? '')
        if (post) {
          return new BehaviorSubject<Post>(post)
        } else if (selectedShortcode) {
          return this.postService.getPost(selectedShortcode)
        } else {
          return new BehaviorSubject(null)
        }
      })
    )
    this.selectedUsername$ = this.route.paramMap.pipe(
      map(paramMap => paramMap.get('username'))
    )
  }

  getNextPage() {
    this.postService.list(this.postService.posts.size, 100, this.username, this.year, this.month).subscribe(response => {
      response.posts.forEach(post => {
        this.postService.posts.set(post.shortcode, post)
      })
    })
  }
}
