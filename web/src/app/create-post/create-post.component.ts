import { Component, OnInit } from '@angular/core';
import { APIService } from '../api.service';

@Component({
  selector: 'app-create-post',
  templateUrl: './create-post.component.html',
  styleUrls: ['./create-post.component.scss']
})
export class CreatePostComponent implements OnInit {
  shortcode?: string;
  constructor(private apiService: APIService) { }

  ngOnInit(): void {
  }

  onSubmit() {
    if (this.shortcode) {
      this.apiService.savePost(this.shortcode);
    }
  }
}
